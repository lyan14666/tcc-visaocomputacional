<?php
declare(strict_types=1);

$host = 'localhost';
$dbname = 'vigia_ai';
$username = 'vigia_app';
$password = 'VigiaLocal_2026_TroqueDepois!';

$pdo = new PDO(
    "mysql:host=$host;dbname=$dbname;charset=utf8mb4",
    $username,
    $password,
    [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]
);
