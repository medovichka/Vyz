package ru.university.lab3.App;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(scanBasePackages = "ru.university.lab3")
@EntityScan(basePackages = "ru.university.lab3.entity")
@EnableJpaRepositories(basePackages = "ru.university.lab3.repository")
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}