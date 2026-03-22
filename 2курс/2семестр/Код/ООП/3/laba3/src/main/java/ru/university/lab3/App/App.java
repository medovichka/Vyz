// src/main/java/com/lab3/App.java
package ru.university.lab3.App;

import ru.university.lab3.dao.Dao;
import ru.university.lab3.entity.*;

import java.util.List;

public class App {
    public static void main(String[] args) {
        Dao dao = new Dao();

        ComOrg kamaz = new ComOrg("КАМАЗ", "1650032058",5000,"5000000","Автопром");
        NonComOrg dobro = new NonComOrg("Добро", "1231231", 1000, "Добро", "TikTOk");
        dao.save(kamaz);
        dao.save(dobro);




        List<Organization> orgs = dao.getAllOrganizations();
        for (Organization o : orgs) {
            System.out.println("  - " + o.getName() + " (ID: " + o.getId() + ")");
        }

        Organization foundKamaz = dao.findOrganizationById(kamaz.getId());
        if (foundKamaz != null) {
            System.out.println("Найден: " + foundKamaz.getName());
        }


        System.out.println("Сотрудников до: " + foundKamaz.getEmployees());
        foundKamaz.hire();
        System.out.println("Сотрудников после: " + foundKamaz.getEmployees());

        dao.update(foundKamaz);
        dao.findOrganizationById(foundKamaz.getId()).report();



        dao.deleteOrganizationById(kamaz.getId());

        System.out.println("\nОставшиеся организации:");
        orgs = dao.getAllOrganizations();
        if (orgs.isEmpty()) {
            System.out.println("  (пусто)");
        } else {
            for (Organization o : orgs) {
                System.out.println("  - " + o.getName());
            }
        }



        for (Organization o : orgs){
            dao.deleteOrganizationById(o.getId());
        }


        dao.close();
    }
}