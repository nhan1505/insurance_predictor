CREATE DATABASE InsurancePredictor;
GO
USE InsurancePredictor;
GO

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100),
    Email NVARCHAR(100) UNIQUE,
    PasswordHash NVARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE(),
    Role NVARCHAR(255)
);

CREATE TABLE Predictions (
    PredictionID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT FOREIGN KEY REFERENCES Users(UserID),
    Age INT NOT NULL,
    Gender BIT NOT NULL,
    BMI FLOAT NOT NULL,
    Smoke BIT NOT NULL,
    Region INT NOT NULL,
    PredictedCost FLOAT NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);

INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES 
(N'Nguyễn Văn A', 'a@gmail.com', '123456', 'user'),
(N'Trần Thị B', 'b@gmail.com', 'abcdef', 'admin');

INSERT INTO Predictions (UserID, Age, Gender, BMI, Smoke, Region, PredictedCost) VALUES 
(1, 30, 1, 25.4, 1, 0, 11500.5),
(2, 45, 0, 29.1, 0, 2, 9800.0);

