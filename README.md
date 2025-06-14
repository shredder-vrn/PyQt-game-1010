🎮 Блок Бласт! (1010-style)
Простая, но увлекательная головоломка в стиле 1010 , написанная на Python с использованием библиотеки PyQt5 .
Игра предлагает размещать фигуры на поле, очищать заполненные строки и столбцы, зарабатывать очки и бороться за рекорды.

🧰 Технологии
Python 3.8+
PyQt5 — библиотека для создания графического интерфейса
QPropertyAnimation — для плавных анимаций
QPainter — для отрисовки блоков и фигур
QColorDialog, QSpinBox — для настройки параметров игры
QPalette — для поддержки светлой и тёмной тем

🎞 Что делает программа?
Отображает игровое поле заданного размера.
Предлагает игроку выбрать одну из трёх случайных фигур.
Позволяет размещать фигуры как кликами мыши, так и перетаскиванием.
При заполнении строк или столбцов они очищаются, начисляется бонус.
Проигрывается анимация размещения и исчезновения блоков.
В конце игры отображается сообщение о результате.
Можно менять настройки: размер поля, цвет блоков, тему оформления.

📦 Основные элементы
Класс Game — управляет логикой игры, хранит состояние поля, очки, список доступных фигур.
Класс BlockWidget — представляет собой ячейку игрового поля, отображает блок с возможностью анимации.
Класс DraggablePieceWidget — виджет для отображения и перетаскивания фигур.
Класс MainWindow — главный интерфейс игры, содержит кнопки, меню и обработчики событий.
Класс SettingsDialog — окно настроек с выбором размера, цвета и темы.

📝 Особенности
Все элементы реализованы в виде отдельных классов (объектно-ориентированный подход).
Анимации реализованы с помощью QPropertyAnimation.
Поддержка двух тем — тёмной и светлой.
Цвета блоков можно сделать одинаковыми или случайными.
Есть возможность расширения: сохранение рекордов, музыка, управление и др.

📌 Возможные доработки
Сохранение рекордов в файл или базу данных.
Добавление фоновой музыки и звуковых эффектов.
Реализация сетевой версии или многопользовательского режима.
Экспорт прогресса или скриншотов.
Поддержка мобильных устройств (например, через Kivy или PySide6 + Android).
