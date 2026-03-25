package ru.university.lab3.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "noncomorganizations")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
public class NonComOrg extends Organization {
    private String purpose;
    private String source;

    public NonComOrg(String name, String inn, int employeesCount, String purpose, String source) {
        this.setName(name);
        this.setInn(inn);
        this.setEmployeesCount(employeesCount);
        this.purpose = purpose;
        this.source = source;
    }

    @Override
    public String report() {
        return "Некоммерческая организация: " + getName()
                + " | ИНН: " + getInn()
                + " | Сотрудники(по штату): " + getEmployeesCount()
                + " | Цель: " + getPurpose()
                + " | Источники: " + getSource();
    }

    @Override
    public int taxes() {
        return getEmployeesCount() * 10;
    }

    public String program(String programName) {
        System.out.println("Запускаем программу: " + programName);
        return programName;
    }

    public String attractFunding(String newSource) {
        System.out.println("Привлекаем финансирование от: " + newSource);
        this.setSource(this.getSource() + ", " + newSource);
        return getSource();
    }
}