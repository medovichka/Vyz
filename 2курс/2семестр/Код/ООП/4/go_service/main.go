package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"strconv"
	"sync"
	"time"
)

type ComOrg struct {
	ID             int    `json:"id"`
	Name           string `json:"name"`
	Inn            string `json:"inn"`
	EmployeesCount int    `json:"employees_count"`
	Profit         string `json:"profit"`
	BusinessType   string `json:"business_type"`
}

type NonComOrg struct {
	ID             int    `json:"id"`
	Name           string `json:"name"`
	Inn            string `json:"inn"`
	EmployeesCount int    `json:"employees_count"`
	Purpose        string `json:"purpose"`
	Source         string `json:"source"`
}

type Employee struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Position string `json:"position"`
	OrgID    int    `json:"org_id"`
}

type OrgOption struct { ID int; Name string }

func (c ComOrg) Taxes() int {
	if c.Profit == "" { return 0 }
	p, err := strconv.Atoi(c.Profit)
	if err != nil { return 0 }
	return p * 20 / 100
}

func (n NonComOrg) Taxes() int { return n.EmployeesCount * 10 }

var cache = make(map[string][]byte)
var expiration = make(map[string]int64)
var cacheMutex sync.RWMutex

func getFromCacheOrFetch(url string) ([]byte, error) {
	cacheMutex.RLock()
	val, found := cache[url]
	exp := expiration[url]
	cacheMutex.RUnlock()

	if found && time.Now().Unix() < exp { return val, nil }

	resp, err := http.Get(url)
	if err != nil { return nil, err }
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

func requestJSON(method string, url string, data interface{}) {
	jsonData, _ := json.Marshal(data)
	req, _ := http.NewRequest(method, url, bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	http.DefaultClient.Do(req)
}

const pythonAPI = "http://localhost:8000/api"

func indexHandler(w http.ResponseWriter, r *http.Request) {
	cd, _ := getFromCacheOrFetch(pythonAPI + "/comorgs")
	nd, _ := getFromCacheOrFetch(pythonAPI + "/noncomorgs")
	ed, _ := getFromCacheOrFetch(pythonAPI + "/employees")

	var comOrgs []ComOrg; json.Unmarshal(cd, &comOrgs)
	var nonComOrgs []NonComOrg; json.Unmarshal(nd, &nonComOrgs)
	var employees []Employee; json.Unmarshal(ed, &employees)

	totalTaxes := 0
	var allOrgs []OrgOption
	for _, o := range comOrgs { totalTaxes += o.Taxes(); allOrgs = append(allOrgs, OrgOption{ID: o.ID, Name: o.Name + " (Ком)"}) }
	for _, o := range nonComOrgs { totalTaxes += o.Taxes(); allOrgs = append(allOrgs, OrgOption{ID: o.ID, Name: o.Name + " (Неком)"}) }

	tmpl := template.Must(template.ParseFiles("templates/index.html"))
	tmpl.Execute(w, map[string]interface{}{ "ComOrgs": comOrgs, "NonComOrgs": nonComOrgs, "Employees": employees, "TotalTaxes": totalTaxes, "AllOrgs": allOrgs })
}

// ========== НОВЫЙ ОБРАБОТЧИК ДЛЯ БИЗНЕС-МЕТОДОВ ==========
func actionHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	action := r.FormValue("action")
	id := r.FormValue("id")
	orgType := r.FormValue("type") // comorgs или noncomorgs

	url := fmt.Sprintf("%s/%s/%s", pythonAPI, orgType, id)

	// 1. Получаем текущую организацию из Python (БД)
	resp, _ := http.Get(url)
	body, _ := io.ReadAll(resp.Body)

	// 2. В зависимости от типа меняем данные и отправляем обратно PUT
	if orgType == "comorgs" {
		var org ComOrg
		json.Unmarshal(body, &org)

		switch action {
		case "hireEmployee":
			org.EmployeesCount++
		case "expandBusiness":
			// Расширение бизнеса: прибыль увеличивается на 20%
			p, _ := strconv.Atoi(org.Profit)
			org.Profit = strconv.Itoa(int(float64(p) * 1.2))
		}
		requestJSON(http.MethodPut, url, org)

	} else if orgType == "noncomorgs" {
		var org NonComOrg
		json.Unmarshal(body, &org)

		switch action {
		case "hireEmployee":
			org.EmployeesCount++
		case "attractFunding":
			// Привлечение финансирования (добавляем строку к источникам)
			newSource := r.FormValue("param")
			if org.Source == "" {
				org.Source = newSource
			} else {
				org.Source = org.Source + ", " + newSource
			}
		}
		requestJSON(http.MethodPut, url, org)
	}

	invalidateCache() // Сбрасываем кэш, чтобы обновить UI
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

// Стандартные CRUD функции
func addComOrgHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	ec, _ := strconv.Atoi(r.FormValue("employeesCount"))
	requestJSON(http.MethodPost, pythonAPI+"/comorgs", ComOrg{Name: r.FormValue("name"), Inn: r.FormValue("inn"), EmployeesCount: ec, Profit: r.FormValue("profit"), BusinessType: r.FormValue("businessType")})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func addNonComOrgHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	ec, _ := strconv.Atoi(r.FormValue("employeesCount"))
	requestJSON(http.MethodPost, pythonAPI+"/noncomorgs", NonComOrg{Name: r.FormValue("name"), Inn: r.FormValue("inn"), EmployeesCount: ec, Purpose: r.FormValue("purpose"), Source: r.FormValue("source")})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func addEmpHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	orgID, _ := strconv.Atoi(r.FormValue("orgId"))
	requestJSON(http.MethodPost, pythonAPI+"/employees", Employee{Name: r.FormValue("name"), Position: r.FormValue("position"), OrgID: orgID})
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func deleteHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	req, _ := http.NewRequest(http.MethodDelete, pythonAPI+"/"+r.FormValue("type")+"/"+r.FormValue("id"), nil)
	http.DefaultClient.Do(req)
	invalidateCache()
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func main() {
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/action", actionHandler) // Наш новый маршрут
	http.HandleFunc("/addComOrg", addComOrgHandler)
	http.HandleFunc("/addNonComOrg", addNonComOrgHandler)
	http.HandleFunc("/addEmp", addEmpHandler)
	http.HandleFunc("/delete", deleteHandler)

	fmt.Println("Go Server is running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}