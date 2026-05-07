package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

type ComOrg struct {
	ID           int    `json:"id"`
	Name         string `json:"name"`
	Inn          string `json:"inn"`
	Profit       string `json:"profit"`
	BusinessType string `json:"business_type"`
}

// Taxes для коммерческих - 20% от прибыли
func (c ComOrg) Taxes() int {
	if c.Profit == "" {
		return 0
	}
	p, err := strconv.Atoi(c.Profit)
	if err != nil || p < 0 {
		return 0
	}
	tax := p * 20 / 100
	if tax < 0 {
		return 0
	}
	return tax
}

type NonComOrg struct {
	ID      int    `json:"id"`
	Name    string `json:"name"`
	Inn     string `json:"inn"`
	Purpose string `json:"purpose"`
	Source  string `json:"source"`
}

type Employee struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Position string `json:"position"`
	OrgID    int    `json:"org_id"`
	OrgName  string `json:"org_name"`
}

type OrgOption struct {
	ID   int
	Name string
}

type ComOrgDisplay struct {
	ComOrg
	EmployeesCount int
	Taxes          int
}

type NonComOrgDisplay struct {
	NonComOrg
	EmployeesCount int
	Taxes          int
}

type TemplateData struct {
	ComOrgs      []ComOrgDisplay
	NonComOrgs   []NonComOrgDisplay
	Employees    []Employee
	AllOrgs      []OrgOption
	NameFilter   string
	MinEmployees int
	MaxEmployees int
}

var cache = make(map[string][]byte)
var expiration = make(map[string]int64)
var cacheMutex sync.RWMutex

func getFromCacheOrFetch(url string) ([]byte, error) {
	cacheMutex.RLock()
	val, found := cache[url]
	exp := expiration[url]
	cacheMutex.RUnlock()

	if found && time.Now().Unix() < exp {
		return val, nil
	}

	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)

	cacheMutex.Lock()
	cache[url] = body
	expiration[url] = time.Now().Add(5 * time.Minute).Unix()
	cacheMutex.Unlock()

	return body, nil
}

func invalidateCache() {
	cacheMutex.Lock()
	cache = make(map[string][]byte)
	cacheMutex.Unlock()
}

func requestJSON(method string, url string, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(method, url, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	_, err = http.DefaultClient.Do(req)
	return err
}

const pythonAPI = "http://localhost:8000"

func countEmployees(employees []Employee, orgID int) int {
	count := 0
	for _, emp := range employees {
		if emp.OrgID == orgID {
			count++
		}
	}
	return count
}

func calculateNonComTax(employeesCount int) int {
	tax := employeesCount * 10
	if tax < 0 {
		return 0
	}
	return tax
}

func filterOrgs(comOrgs []ComOrgDisplay, nonComOrgs []NonComOrgDisplay, nameFilter string, minEmp, maxEmp int) ([]ComOrgDisplay, []NonComOrgDisplay) {
	filteredCom := []ComOrgDisplay{}
	filteredNon := []NonComOrgDisplay{}

	for _, org := range comOrgs {
		if nameFilter != "" && !strings.Contains(strings.ToLower(org.Name), strings.ToLower(nameFilter)) {
			continue
		}
		if minEmp > 0 && org.EmployeesCount < minEmp {
			continue
		}
		if maxEmp > 0 && org.EmployeesCount > maxEmp {
			continue
		}
		filteredCom = append(filteredCom, org)
	}

	for _, org := range nonComOrgs {
		if nameFilter != "" && !strings.Contains(strings.ToLower(org.Name), strings.ToLower(nameFilter)) {
			continue
		}
		if minEmp > 0 && org.EmployeesCount < minEmp {
			continue
		}
		if maxEmp > 0 && org.EmployeesCount > maxEmp {
			continue
		}
		filteredNon = append(filteredNon, org)
	}

	return filteredCom, filteredNon
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	nameFilter := r.URL.Query().Get("nameFilter")
	minEmp, _ := strconv.Atoi(r.URL.Query().Get("minEmployees"))
	maxEmp, _ := strconv.Atoi(r.URL.Query().Get("maxEmployees"))

	cd, _ := getFromCacheOrFetch(pythonAPI + "/api/comorgs")
	nd, _ := getFromCacheOrFetch(pythonAPI + "/api/noncomorgs")
	ed, _ := getFromCacheOrFetch(pythonAPI + "/api/employees")

	var comOrgs []ComOrg
	var nonComOrgs []NonComOrg
	var employees []Employee
	json.Unmarshal(cd, &comOrgs)
	json.Unmarshal(nd, &nonComOrgs)
	json.Unmarshal(ed, &employees)

	orgNameMap := make(map[int]string)
	for _, org := range comOrgs {
		orgNameMap[org.ID] = org.Name + " (Ком)"
	}
	for _, org := range nonComOrgs {
		orgNameMap[org.ID] = org.Name + " (Неком)"
	}

	for i := range employees {
		if name, ok := orgNameMap[employees[i].OrgID]; ok {
			employees[i].OrgName = name
		} else {
			employees[i].OrgName = ""
		}
	}

	var comOrgsDisplay []ComOrgDisplay
	for _, org := range comOrgs {
		empCount := countEmployees(employees, org.ID)
		comOrgsDisplay = append(comOrgsDisplay, ComOrgDisplay{
			ComOrg:         org,
			EmployeesCount: empCount,
			Taxes:          org.Taxes(),
		})
	}

	var nonComOrgsDisplay []NonComOrgDisplay
	for _, org := range nonComOrgs {
		empCount := countEmployees(employees, org.ID)
		nonComOrgsDisplay = append(nonComOrgsDisplay, NonComOrgDisplay{
			NonComOrg:      org,
			EmployeesCount: empCount,
			Taxes:          calculateNonComTax(empCount),
		})
	}

	filteredCom, filteredNon := filterOrgs(comOrgsDisplay, nonComOrgsDisplay, nameFilter, minEmp, maxEmp)

	var allOrgs []OrgOption
	for _, o := range comOrgs {
		allOrgs = append(allOrgs, OrgOption{ID: o.ID, Name: o.Name + " (Ком)"})
	}
	for _, o := range nonComOrgs {
		allOrgs = append(allOrgs, OrgOption{ID: o.ID, Name: o.Name + " (Неком)"})
	}

	data := TemplateData{
		ComOrgs:      filteredCom,
		NonComOrgs:   filteredNon,
		Employees:    employees,
		AllOrgs:      allOrgs,
		NameFilter:   nameFilter,
		MinEmployees: minEmp,
		MaxEmployees: maxEmp,
	}

	tmpl := template.Must(template.ParseFiles("templates/index.html"))
	tmpl.Execute(w, data)
}

func getOrgHandler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	orgType := r.URL.Query().Get("type")
	url := fmt.Sprintf("%s/api/%s/%s", pythonAPI, orgType, id)
	resp, err := http.Get(url)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	w.Header().Set("Content-Type", "application/json")
	w.Write(body)
}

func editHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	id := r.FormValue("id")
	orgType := r.FormValue("type")
	url := fmt.Sprintf("%s/api/%s/%s", pythonAPI, orgType, id)

	if orgType == "comorgs" {
		profit := r.FormValue("profit")
		if profitInt, err := strconv.Atoi(profit); err != nil || profitInt < 0 {
			profit = "0"
		}

		org := ComOrg{
			Name:         r.FormValue("name"),
			Inn:          r.FormValue("inn"),
			Profit:       profit,
			BusinessType: r.FormValue("businessType"),
		}
		requestJSON(http.MethodPut, url, org)
	} else if orgType == "noncomorgs" {
		org := NonComOrg{
			Name:    r.FormValue("name"),
			Inn:     r.FormValue("inn"),
			Purpose: r.FormValue("purpose"),
			Source:  r.FormValue("source"),
		}
		requestJSON(http.MethodPut, url, org)
	}
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func actionHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	action := r.FormValue("action")
	id := r.FormValue("id")
	orgType := r.FormValue("type")
	url := fmt.Sprintf("%s/api/%s/%s", pythonAPI, orgType, id)

	resp, err := http.Get(url)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	if orgType == "comorgs" {
		var org ComOrg
		json.Unmarshal(body, &org)
		switch action {
		case "expandBusiness":
			p, _ := strconv.Atoi(org.Profit)
			newProfit := int(float64(p) * 1.2)
			if newProfit < 0 {
				newProfit = 0
			}
			org.Profit = strconv.Itoa(newProfit)
			requestJSON(http.MethodPut, url, org)
		}
	} else if orgType == "noncomorgs" {
		var org NonComOrg
		json.Unmarshal(body, &org)
		switch action {
		case "attractFunding":
			newSource := r.FormValue("param")
			if org.Source == "" {
				org.Source = newSource
			} else {
				org.Source = org.Source + ", " + newSource
			}
			requestJSON(http.MethodPut, url, org)
		}
	}
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

type OrgEmployeesResponse struct {
	Success   bool   `json:"success"`
	OrgName   string `json:"orgName"`
	Employees []struct {
		ID       int    `json:"id"`
		Name     string `json:"name"`
		Position string `json:"position"`
	} `json:"employees"`
}

func getOrgEmployeesHandler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	orgType := r.URL.Query().Get("type")

	if id == "" || orgType == "" {
		http.Error(w, "Не указаны ID или тип организации", http.StatusBadRequest)
		return
	}

	orgID, err := strconv.Atoi(id)
	if err != nil {
		http.Error(w, "ID должен быть числом", http.StatusBadRequest)
		return
	}

	url := fmt.Sprintf("%s/api/getOrgEmployees", pythonAPI)

	requestBody := map[string]interface{}{
		"id":   orgID,
		"type": orgType,
	}
	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(body)
}

func addComOrgHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()

	profit := r.FormValue("profit")
	if profitInt, err := strconv.Atoi(profit); err != nil || profitInt < 0 {
		profit = "0"
	}

	requestJSON(http.MethodPost, pythonAPI+"/api/comorgs", ComOrg{
		Name:         r.FormValue("name"),
		Inn:          r.FormValue("inn"),
		Profit:       profit,
		BusinessType: r.FormValue("businessType"),
	})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func addNonComOrgHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()

	requestJSON(http.MethodPost, pythonAPI+"/api/noncomorgs", NonComOrg{
		Name:    r.FormValue("name"),
		Inn:     r.FormValue("inn"),
		Purpose: r.FormValue("purpose"),
		Source:  r.FormValue("source"),
	})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func getEmployeeHandler(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	url := fmt.Sprintf("%s/api/employees/%s", pythonAPI, id)
	resp, err := http.Get(url)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	w.Header().Set("Content-Type", "application/json")
	w.Write(body)
}

func editEmployeeHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	id := r.FormValue("id")
	orgID, _ := strconv.Atoi(r.FormValue("orgId"))

	url := fmt.Sprintf("%s/api/employees/%s", pythonAPI, id)
	requestJSON(http.MethodPut, url, Employee{
		Name:     r.FormValue("name"),
		Position: r.FormValue("position"),
		OrgID:    orgID,
	})

	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func addEmpHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	orgID, _ := strconv.Atoi(r.FormValue("orgId"))
	requestJSON(http.MethodPost, pythonAPI+"/api/employees", Employee{
		Name:     r.FormValue("name"),
		Position: r.FormValue("position"),
		OrgID:    orgID,
	})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func deleteHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	req, _ := http.NewRequest(http.MethodDelete, pythonAPI+"/api/"+r.FormValue("type")+"/"+r.FormValue("id"), nil)
	http.DefaultClient.Do(req)
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func deleteEmployeeHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	id := r.FormValue("id")
	req, _ := http.NewRequest(http.MethodDelete, pythonAPI+"/api/employees/"+id, nil)
	http.DefaultClient.Do(req)
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func main() {
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/getOrg", getOrgHandler)
	http.HandleFunc("/edit", editHandler)
	http.HandleFunc("/action", actionHandler)
	http.HandleFunc("/addComOrg", addComOrgHandler)
	http.HandleFunc("/addNonComOrg", addNonComOrgHandler)
	http.HandleFunc("/addEmp", addEmpHandler)
	http.HandleFunc("/delete", deleteHandler)
	http.HandleFunc("/deleteEmployee", deleteEmployeeHandler)
	http.HandleFunc("/getEmployee", getEmployeeHandler)
	http.HandleFunc("/getOrgEmployees", getOrgEmployeesHandler)
	http.HandleFunc("/editEmployee", editEmployeeHandler)

	fmt.Println("Go Server is running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}