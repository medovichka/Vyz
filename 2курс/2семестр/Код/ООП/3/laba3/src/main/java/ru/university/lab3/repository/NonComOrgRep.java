package ru.university.lab3.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import ru.university.lab3.entity.NonComOrg;

@Repository
public interface NonComOrgRep extends JpaRepository<NonComOrg, Integer> {
}