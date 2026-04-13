package ru.university.lab3.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import ru.university.lab3.entity.Organization;

@Repository
public interface OrganizationRep extends JpaRepository<Organization, Integer> {
}