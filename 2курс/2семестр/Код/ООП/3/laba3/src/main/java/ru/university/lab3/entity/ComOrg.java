package ru.university.lab3.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "comorganizations")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
public class ComOrg extends Organization {
    private String profit;
    private String businessType;
    public ComOrg(String name, String inn, int employees, String profit, String businessType) {
        this.setName(name);
        this.setInn(inn);
        this.setEmployees(employees);
        this.profit = profit;
        this.businessType = businessType;
    }
    @Override
    public String report() {
        return "Коммерческая организация:" + getName()
                + "ИНН:" + getInn()
                + "Тип:" + getBusinessType()
                + "Сотрудники:" + getEmployees()
                + "\nПрибыль:" + getProfit();
    }

    @Override
    public int taxes() {
        if (this.profit == null || this.profit.isEmpty()) {
            return 0;
        }
        try {
            int Value = Integer.parseInt(this.profit);
            return Value * 20 / 100; // налог с прибыли
        } catch (NumberFormatException e) {
            return 0; // прибыль не число
        }
    }

    public String expandBusiness() {
        try {
            int profitValue = Integer.parseInt(this.profit);
            profitValue = profitValue + (int) (profitValue * 0.20);
            return String.valueOf(profitValue);
        } catch (NumberFormatException e) {
            return this.profit;
        }
    }

    public String distribute() {
        try {
            int profitValue = Integer.parseInt(this.profit);
            profitValue = profitValue / 22 * 3;
            return String.valueOf(profitValue);
        } catch (NumberFormatException e) {
            return "0";
        }
    }
}