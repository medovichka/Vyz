package ru.university.lab3.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import ru.university.lab3.dao.Dao;
import ru.university.lab3.entity.ComOrg;
import ru.university.lab3.entity.Employees;
import ru.university.lab3.entity.NonComOrg;
import ru.university.lab3.entity.Organization;

@Controller
public class WebController {

    private final Dao dao = new Dao();

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("organizations", dao.getAllOrganizations());
        model.addAttribute("employees", dao.getAllEmployees());
        return "index";
    }

    // ================= УДАЛЕНИЕ (DELETE) =================

    @PostMapping("/deleteOrg")
    public String deleteOrg(@RequestParam int id) {
        dao.deleteOrganizationById(id);
        return "redirect:/";
    }

    @PostMapping("/deleteEmp")
    public String deleteEmp(@RequestParam int id) {
        dao.deleteEmployeeById(id);
        return "redirect:/";
    }

    // ================= ДОБАВЛЕНИЕ (CREATE) =================

    @PostMapping("/addComOrg")
    public String addComOrg(@RequestParam String name, @RequestParam String inn,
                            @RequestParam int employeesCount, @RequestParam String profit,
                            @RequestParam String businessType) {
        ComOrg org = new ComOrg(name, inn, employeesCount, profit, businessType);
        dao.save(org);
        return "redirect:/";
    }

    @PostMapping("/addNonComOrg")
    public String addNonComOrg(@RequestParam String name, @RequestParam String inn,
                               @RequestParam int employeesCount, @RequestParam String purpose,
                               @RequestParam String source) {
        NonComOrg org = new NonComOrg(name, inn, employeesCount, purpose, source);
        dao.save(org);
        return "redirect:/";
    }

    @PostMapping("/addEmp")
    public String addEmp(@RequestParam String name, @RequestParam String position,
                         @RequestParam(required = false, defaultValue = "0") int orgId) {
        Employees emp = new Employees(name, position);
        if (orgId > 0) {
            Organization org = dao.findOrganizationById(orgId);
            if (org != null) emp.setOrganization(org);
        }
        dao.save(emp);
        return "redirect:/";
    }

    // ================= РЕДАКТИРОВАНИЕ (UPDATE) =================

    @PostMapping("/updateComOrg")
    public String updateComOrg(@RequestParam int id, @RequestParam String name, @RequestParam String inn,
                               @RequestParam int employeesCount, @RequestParam String profit,
                               @RequestParam String businessType) {
        Organization baseOrg = dao.findOrganizationById(id);
        if (baseOrg instanceof ComOrg org) {
            org.setName(name);
            org.setInn(inn);
            org.setEmployeesCount(employeesCount);
            org.setProfit(profit);
            org.setBusinessType(businessType);
            dao.update(org);
        }
        return "redirect:/";
    }

    @PostMapping("/updateNonComOrg")
    public String updateNonComOrg(@RequestParam int id, @RequestParam String name, @RequestParam String inn,
                                  @RequestParam int employeesCount, @RequestParam String purpose,
                                  @RequestParam String source) {
        Organization baseOrg = dao.findOrganizationById(id);
        if (baseOrg instanceof NonComOrg org) {
            org.setName(name);
            org.setInn(inn);
            org.setEmployeesCount(employeesCount);
            org.setPurpose(purpose);
            org.setSource(source);
            dao.update(org);
        }
        return "redirect:/";
    }

    @PostMapping("/updateEmp")
    public String updateEmp(@RequestParam int id, @RequestParam String name, @RequestParam String position,
                            @RequestParam(required = false, defaultValue = "0") int orgId) {
        Employees emp = dao.findEmployeeById(id);
        if (emp != null) {
            emp.setName(name);
            emp.setPosition(position);

            if (orgId > 0) {
                Organization org = dao.findOrganizationById(orgId);
                emp.setOrganization(org);
            } else {
                emp.setOrganization(null); // Если выбрали "Без организации"
            }
            dao.update(emp);
        }
        return "redirect:/";
    }
}