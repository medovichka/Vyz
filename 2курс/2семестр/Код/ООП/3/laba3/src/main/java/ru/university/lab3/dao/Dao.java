package ru.university.lab3.dao;

import org.hibernate.Hibernate;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.cfg.Configuration;
import ru.university.lab3.entity.Employees;
import ru.university.lab3.entity.Organization;
import java.util.ArrayList;
import java.util.List;

public class Dao {
    private final SessionFactory sessionFactory;

    public Dao() {
        sessionFactory = new Configuration().configure().buildSessionFactory();
    }

    public void save(Object obj) {
        Transaction tx = null;
        try (Session session = sessionFactory.openSession()) {
            tx = session.beginTransaction();
            session.persist(obj);
            tx.commit();
        } catch (Exception e) {
            if (tx != null)
                tx.rollback();
            e.printStackTrace();
        }
    }

    public Organization findOrganizationById(int id) {
        try (Session session = sessionFactory.openSession()) {
            Organization org = session.get(Organization.class, id);

            if (org != null) {
                Hibernate.initialize(org.getEmployeesList());
            }

            return org;
        }
    }

    public Employees findEmployeeById(int id) {
        try (Session session = sessionFactory.openSession()) {
            return session.get(Employees.class, id);
        }
    }

    public List<Employees> getEmployeesByOrganizationId(int orgId) {
        try (Session session = sessionFactory.openSession()) {
            Organization org = session.get(Organization.class, orgId);
            if (org == null) {
                return List.of();
            }
            Hibernate.initialize(org.getEmployeesList());
            return new ArrayList<>(org.getEmployeesList());
        }
    }

    public List<Organization> getAllOrganizations() {
        try (Session session = sessionFactory.openSession()) {

            var cb = session.getCriteriaBuilder();
            var cq = cb.createQuery(Organization.class);
            var root = cq.from(Organization.class);

            cq.select(root);

            List<Organization> list = session.createQuery(cq).getResultList();

            for (Organization org : list) {
                Hibernate.initialize(org.getEmployeesList());
            }

            return new ArrayList<>(list);
        }
    }

    public List<Employees> getAllEmployees() {
        try (Session session = sessionFactory.openSession()) {

            var cb = session.getCriteriaBuilder();
            var cq = cb.createQuery(Employees.class);
            var root = cq.from(Employees.class);

            cq.select(root);

            List<Employees> list = session.createQuery(cq).getResultList();

            return new ArrayList<>(list);
        }
    }

    public void update(Object obj) {
        Transaction tx = null;
        try (Session session = sessionFactory.openSession()) {
            tx = session.beginTransaction();
            session.merge(obj);
            tx.commit();
        } catch (Exception e) {
            if (tx != null)
                tx.rollback();
            e.printStackTrace();
        }
    }

    public void deleteOrganizationById(int id) {
        Transaction tx = null;
        try (Session session = sessionFactory.openSession()) {
            tx = session.beginTransaction();

            Organization org = session.get(Organization.class, id);

            if (org != null) {
                session.remove(org);
            }

            tx.commit();
        } catch (Exception e) {
            if (tx != null)
                tx.rollback();
            e.printStackTrace();
        }
    }

    public void deleteEmployeeById(int id) {
        Transaction tx = null;
        try (Session session = sessionFactory.openSession()) {
            tx = session.beginTransaction();

            Employees emp = session.get(Employees.class, id);

            if (emp != null) {
                session.remove(emp);
            }

            tx.commit();
        } catch (Exception e) {
            if (tx != null)
                tx.rollback();
            e.printStackTrace();
        }
    }

    public void close() {
        if (sessionFactory != null) {
            sessionFactory.close();
        }
    }
}