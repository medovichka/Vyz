package ru.university.lab3.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
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

    public ComOrg(String name, String inn, int employeesCount, String profit, String businessType) {
        this.setName(name);
        this.setInn(inn);
        this.setEmployeesCount(employeesCount);
        this.profit = profit;
        this.businessType = businessType;
    }

    @Override
    public String report() {
        return "Коммерческая организация: " + getName()
                + " | ИНН: " + getInn()
                + " | Тип: " + getBusinessType()
                + " | Сотрудники(по штату): " + getEmployeesCount()
                + " | Прибыль: " + getProfit();
    }

    @Override
    public int taxes() {
        if (this.profit == null || this.profit.isEmpty()) {
            return 0;
        }
        try {
            int value = Integer.parseInt(this.profit);
            return value * 20 / 100; // налог с прибыли
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