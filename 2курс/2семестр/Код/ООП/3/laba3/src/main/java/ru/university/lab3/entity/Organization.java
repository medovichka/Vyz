package ru.university.lab3.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "organizations")
@Inheritance(strategy = InheritanceType.JOINED)
@Data
public abstract class Organization {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    private String name;
    private String inn;
    private int employeesCount;

    @OneToMany(mappedBy = "organization", cascade = CascadeType.ALL, orphanRemoval = true)
    @ToString.Exclude
    @EqualsAndHashCode.Exclude
    private List<Employees> employeesList = new ArrayList<>();

    public abstract String report();

    public abstract int taxes();

    public String reklama() {
        return this.name + " оч крутая!";
    }

    public void addEmployee(Employees employee) {
        employeesList.add(employee);
        employee.setOrganization(this);
    }

    public void removeEmployee(Employees employee) {
        employeesList.remove(employee);
        employee.setOrganization(null);
    }
}