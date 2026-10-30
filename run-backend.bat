@echo off
echo ========================================================
echo   PageTurner Online Bookstore - Spring Boot Backend
echo ========================================================
echo.
echo Checking for Maven / Java...
where mvn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found Maven on system PATH. Starting Spring Boot...
    mvn spring-boot:run
) else (
    echo 'mvn' command was not found in PATH.
    echo Please install Java 17+ and Apache Maven, or open this folder in
    echo VS Code / IntelliJ IDEA / Eclipse to run BookstoreApplication.java directly.
    pause
)
