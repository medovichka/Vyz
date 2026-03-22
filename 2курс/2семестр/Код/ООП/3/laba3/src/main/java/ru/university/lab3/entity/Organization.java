package ru.university.lab3.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "organizations")
@Inheritance(strategy = InheritanceType.JOINED)
@Data
public abstract class Organization{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    private String name;
    private String inn;
    private int employees;

    public abstract String report();

    public void hire() {
        this.employees += 22;
    }

    public String reklama() {
        return this.name + " оч крутая!";
    }

    public abstract int taxes();
}
