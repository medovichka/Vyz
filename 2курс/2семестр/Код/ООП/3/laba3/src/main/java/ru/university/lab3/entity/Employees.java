package ru.university.lab3.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.ToString;

@Entity
@Table(name = "employees")
@Data
@NoArgsConstructor
public class Employees {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;
    private String name;
    private String position;

    @ManyToOne
    @JoinColumn(name = "org_id")
    @ToString.Exclude
    @EqualsAndHashCode.Exclude
    private Organization organization;

    public Employees(String name, String position) {
        this.name = name;
        this.position = position;
    }
}