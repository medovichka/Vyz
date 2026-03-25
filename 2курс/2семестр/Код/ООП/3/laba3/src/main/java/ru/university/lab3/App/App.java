package ru.university.lab3.App;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

// ДОБАВЛЕНА НАСТРОЙКА СКАНИРОВАНИЯ!
@SpringBootApplication(scanBasePackages = "ru.university.lab3")
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}