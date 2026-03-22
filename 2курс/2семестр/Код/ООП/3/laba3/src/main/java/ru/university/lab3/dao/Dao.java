// src/main/java/com/lab3/dao/OrganizationDAO.java
package ru.university.lab3.dao;

import ru.university.lab3.entity.*;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.cfg.Configuration;
import java.util.List;

public class Dao {
    // SessionFactory - "фабрика" для создания сессий. Создается один раз.
    private final SessionFactory sessionFactory;

    public Dao() {
        // Загружаем конфигурацию из hibernate.cfg.xml и строим SessionFactory
        sessionFactory = new Configuration().configure().buildSessionFactory();
    }

    //CREATE

    public void save(Object obj) { // Универсальный метод для сохранения любого объекта
        Session session = sessionFactory.openSession();
        Transaction tx = null;
        try {
            tx = session.beginTransaction();
            session.persist(obj); // persist - современный метод для сохранения
            tx.commit();
        } catch (Exception e) {
            if (tx != null) tx.rollback(); // Если ошибка, откатываем транзакцию
            e.printStackTrace();
        } finally {
            session.close(); // Всегда закрываем сессию
        }
    }

    //READ

    public Organization findOrganizationById(int id) {
        Session session = sessionFactory.openSession();
        Organization org = session.get(Organization.class, id);
        session.close();
        return org;
    }

    public List<Organization> getAllOrganizations() {
        Session session = sessionFactory.openSession();
        List<Organization> list = session.createQuery("FROM Organization", Organization.class).list();
        session.close();
        return list;
    }

    // UPDATE

    public void update(Organization org) {
        Session session = sessionFactory.openSession();
        Transaction tx = null;
        try {
            tx = session.beginTransaction();
            session.merge(org);
            tx.commit();
        } catch (Exception e) {
            if (tx != null) tx.rollback();
            e.printStackTrace();
        } finally {
            session.close();
        }
    }

    //DELETE

    public void deleteOrganizationById(int id) {
        Session session = sessionFactory.openSession();
        Transaction tx = null;
        try {
            tx = session.beginTransaction();
            Organization org = session.get(Organization.class, id);
            if (org != null) {
                session.remove(org);
            }
            tx.commit();
        } catch (Exception e) {
            if (tx != null) tx.rollback();
            e.printStackTrace();
        } finally {
            session.close();
        }
    }

    public void close() {
        sessionFactory.close();
    }
}