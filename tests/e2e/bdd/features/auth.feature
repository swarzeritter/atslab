Feature: Автентифікація

  Scenario: Реєстрація нового користувача
    Given браузер відкрито
    When я реєструюсь з іменем "bddnewuser" email "bddnew@test.com" паролем "bdd12345"
    Then я знаходжусь на сторінці постів

  Scenario: Вхід з невірним паролем
    Given браузер відкрито
    When я намагаюсь увійти з email "bddtest@test.com" та паролем "wrongpass"
    Then я знаходжусь на сторінці входу

  Scenario: Успішний вхід
    Given браузер відкрито
    When я входжу з email "bddtest@test.com" та паролем "bdd12345"
    Then я знаходжусь на сторінці постів

  Scenario: Вихід з системи
    Given я авторизований
    When я виходжу з системи
    Then я знаходжусь на сторінці постів
