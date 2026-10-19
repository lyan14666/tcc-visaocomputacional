<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

try {
    require __DIR__ . '/../includes/db.php';

    $stmt = $pdo->query(
        "SELECT id, tipo, camera, confianca, track_id, criado_em
         FROM eventos
         WHERE criado_em >= CURDATE()
         ORDER BY criado_em DESC
         LIMIT 50"
    );

    $total = $pdo->query(
        "SELECT COUNT(*) FROM eventos WHERE criado_em >= CURDATE()"
    )->fetchColumn();

    echo json_encode([
        'sucesso' => true,
        'total_hoje' => (int) $total,
        'eventos' => $stmt->fetchAll()
    ], JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
} catch (Throwable $e) {
    error_log('Falha ao consultar eventos VIGIA AI: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'sucesso' => false,
        'erro' => 'Falha ao consultar eventos'
    ]);
}
