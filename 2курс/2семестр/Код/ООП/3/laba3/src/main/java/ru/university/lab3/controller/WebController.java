package ru.university.lab3.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import ru.university.lab3.entity.*;
import ru.university.lab3.repository.*;

import java.util.Optional;
import java.util.List;

@Controller
public class WebController {

    @Autowired
    private OrganizationRep organizationRep;

    @Autowired
    private ComOrgRep comOrgRep;

    @Autowired
    private NonComOrgRep nonComOrgRep;

    @Autowired
    private EmployeesRep employeesRep;

    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("organizations", organizationRep.findAll());
        model.addAttribute("employees", employeesRep.findAll());
        return "index";
    }

    @GetMapping("/showOrgEmployees")
    public String showOrgEmployees(@RequestParam int id,Model model) {
        Organization org = organizationRep.findById(id).orElse(null);
        List<Employees> emp = org.getEmployeesList();
        model.addAttribute("organization", org);
        model.addAttribute("employees", emp);
        return "employeesList";
    }




    // ================= УДАЛЕНИЕ =================

    @PostMapping("/deleteOrg")
    public String deleteOrg(@RequestParam int id) {
        organizationRep.deleteById(id);
        return "redirect:/";
    }

    @PostMapping("/deleteEmp")
    public String deleteEmp(@RequestParam int id) {
        employeesRep.deleteById(id);
        return "redirect:/";
    }

    // ================= ДОБАВЛЕНИЕ =================

    @PostMapping("/addComOrg")
    public String addComOrg(@RequestParam String name, @RequestParam String inn,
                            @RequestParam int employeesCount, @RequestParam String profit,
                            @RequestParam String businessType) {
        ComOrg org = new ComOrg(name, inn, employeesCount, profit, businessType);
        comOrgRep.save(org);
        return "redirect:/";
    }

    @PostMapping("/addNonComOrg")
    public String addNonComOrg(@RequestParam String name, @RequestParam String inn,
                               @RequestParam int employeesCount, @RequestParam String purpose,
                               @RequestParam String source) {
        NonComOrg org = new NonComOrg(name, inn, employeesCount, purpose, source);
        nonComOrgRep.save(org);
        return "redirect:/";
    }

    @PostMapping("/addEmp")
    public String addEmp(@RequestParam String name, @RequestParam String position,
                         @RequestParam(required = false, defaultValue = "0") int orgId) {
        Employees emp = new Employees(name, position);
        if (orgId > 0) {
            Optional<Organization> org = organizationRep.findById(orgId);
            org.ifPresent(emp::setOrganization);
        }
        employeesRep.save(emp);
        return "redirect:/";
    }

    // ================= РЕДАКТИРОВАНИЕ =================

    @PostMapping("/updateComOrg")
    public String updateComOrg(@RequestParam int id, @RequestParam String name,
                               @RequestParam String inn, @RequestParam int employeesCount,
                               @RequestParam String profit, @RequestParam String businessType) {
        Optional<ComOrg> optionalOrg = comOrgRep.findById(id);
        if (optionalOrg.isPresent()) {
            ComOrg org = optionalOrg.get();
            org.setName(name);
            org.setInn(inn);
            org.setEmployeesCount(employeesCount);
            org.setProfit(profit);
            org.setBusinessType(businessType);
            comOrgRep.save(org);
        }
        return "redirect:/";
    }

    @PostMapping("/updateNonComOrg")
    public String updateNonComOrg(@RequestParam int id, @RequestParam String name,
                                  @RequestParam String inn, @RequestParam int employeesCount,
                                  @RequestParam String purpose, @RequestParam String source) {
        Optional<NonComOrg> optionalOrg = nonComOrgRep.findById(id);
        if (optionalOrg.isPresent()) {
            NonComOrg org = optionalOrg.get();
            org.setName(name);
            org.setInn(inn);
            org.setEmployeesCount(employeesCount);
            org.setPurpose(purpose);
            org.setSource(source);
            nonComOrgRep.save(org);
        }
        return "redirect:/";
    }

    @PostMapping("/updateEmp")
    public String updateEmp(@RequestParam int id, @RequestParam String name,
                            @RequestParam String position,
                            @RequestParam(required = false, defaultValue = "0") int orgId) {
        Optional<Employees> optionalEmp = employeesRep.findById(id);
        if (optionalEmp.isPresent()) {
            Employees emp = optionalEmp.get();
            emp.setName(name);
            emp.setPosition(position);

            if (orgId > 0) {
                organizationRep.findById(orgId).ifPresent(emp::setOrganization);
            } else {
                emp.setOrganization(null);
            }
            employeesRep.save(emp);
        }
        return "redirect:/";
    }
}