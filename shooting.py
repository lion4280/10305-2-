<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>스페이스 슈팅 - 인페르노 모드</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            user-select: none;
        }
        canvas {
            background-color: black;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
            border-radius: 4px;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="500" height="700"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = 500;
const HEIGHT = 700;

// 게임 상태 변수
let score = 0;
let bombs = 2;
let powerUpTimer = 0;
let frameCount = 0;
let difficultyLevel = 1;
let gameOver = false;
let showIntro = true;
let flashTimer = 0;

// 플레이어 설정
const player = {
    x: 250,
    y: 640,
    width: 40,
    height: 40,
    speed: 8,
    color: "cyan"
};

let bullets = [];
let enemyBullets = [];
let enemies = [];
let items = [];

const keyPressed = {
    left: false,
    right: false
};

// 키 이벤트 리스너
window.addEventListener("keydown", (e) => {
    const key = e.key.toLowerCase();
    
    if (key === "arrowleft" || key === "a") {
        keyPressed.left = true;
    } else if (key === "arrowright" || key === "d") {
        keyPressed.right = true;
    } else if (e.code === "Space" && !gameOver) {
        e.preventDefault();
        fireBullet();
    } else if (key === "b" && !gameOver) {
        useBomb();
    } else if (key === "r" && gameOver) {
        restartGame();
    }
});

window.addEventListener("keyup", (e) => {
    const key = e.key.toLowerCase();
    if (key === "arrowleft" || key === "a") {
        keyPressed.left = false;
    } else if (key === "arrowright" || key === "d") {
        keyPressed.right = false;
    }
});

function fireBullet() {
    showIntro = false;
    const px = player.x;
    const py = player.y - 20;

    if (powerUpTimer > 0) {
        bullets.push({ x: px - 12, y: py, width: 6, height: 10, dx: -3, color: "lime" });
        bullets.push({ x: px,      y: py - 5, width: 6, height: 15, dx: 0,  color: "yellow" });
        bullets.push({ x: px + 12, y: py, width: 6, height: 10, dx: 3,  color: "lime" });
    } else {
        bullets.push({ x: px, y: py - 5, width: 6, height: 15, dx: 0, color: "yellow" });
    }
}

function useBomb() {
    if (bombs > 0 && (enemies.length > 0 || enemyBullets.length > 0)) {
        bombs--;
        score += enemies.length * 20;
        enemies = [];
        enemyBullets = [];
        flashTimer = 5; // 화면 플래시 프레임 수
    }
}

function spawnEnemy() {
    if (gameOver) return;
    
    const x = Math.random() * (WIDTH - 80) + 40;
    if (Math.random() < 0.25) {
        // 보스형 적
        enemies.push({
            x: x,
            y: -50,
            width: 50,
            height: 40,
            hp: 3 + Math.floor(difficultyLevel / 3),
            type: "boss"
        });
    } else {
        // 일반형 적
        enemies.push({
            x: x,
            y: -36,
            width: 36,
            height: 36,
            hp: 1,
            type: "normal"
        });
    }
}

// AABB 충돌 감지
function checkCollision(r1, r2) {
    return !(
        r1.x + r1.width / 2 < r2.x - r2.width / 2 ||
        r1.x - r1.width / 2 > r2.x + r2.width / 2 ||
        r1.y + r1.height / 2 < r2.y - r2.height / 2 ||
        r1.y - r1.height / 2 > r2.y + r2.height / 2
    );
}

function endGame() {
    gameOver = true;
    player.color = "red";
}

function restartGame() {
    bullets = [];
    enemyBullets = [];
    enemies = [];
    items = [];
    keyPressed.left = false;
    keyPressed.right = false;

    score = 0;
    bombs = 2;
    powerUpTimer = 0;
    frameCount = 0;
    difficultyLevel = 1;
    gameOver = false;
    showIntro = false;
    player.x = 250;
    player.y = 640;
    player.color = "cyan";
}

function update() {
    if (gameOver) return;

    // 난이도 상승 (약 6초 = 300프레임)
    frameCount++;
    if (frameCount % 300 === 0) {
        difficultyLevel++;
    }

    // 파워업 타이머
    if (powerUpTimer > 0) {
        powerUpTimer--;
    }

    // 플레이어 이동
    if (keyPressed.left && player.x - 20 > 20) {
        player.x -= player.speed;
        showIntro = false;
    }
    if (keyPressed.right && player.x + 20 < WIDTH - 20) {
        player.x += player.speed;
        showIntro = false;
    }

    // 아군 총알 이동
    for (let i = bullets.length - 1; i >= 0; i--) {
        const b = bullets[i];
        b.x += b.dx;
        b.y -= 12;
        if (b.y < -20) {
            bullets.splice(i, 1);
        }
    }

    // 적 총알 이동 및 충돌
    const ebSpeed = 6 + difficultyLevel;
    for (let i = enemyBullets.length - 1; i >= 0; i--) {
        const eb = enemyBullets[i];
        eb.y += ebSpeed;

        if (checkCollision(player, eb)) {
            endGame();
            return;
        }

        if (eb.y > HEIGHT + 20) {
            enemyBullets.splice(i, 1);
        }
    }

    // 적 로직
    const baseEnemySpeed = 3 + (difficultyLevel * 0.5);
    for (let i = enemies.length - 1; i >= 0; i--) {
        const e = enemies[i];
        const speed = (e.type === "boss") ? baseEnemySpeed : baseEnemySpeed + 2;
        e.y += speed;

        // 적 발사 확률
        const shootChance = 0.01 + (difficultyLevel * 0.005);
        if (Math.random() < shootChance) {
            enemyBullets.push({
                x: e.x,
                y: e.y + e.height / 2,
                width: 6,
                height: 12
            });
        }

        // 아군 총알과 적 충돌
        for (let j = bullets.length - 1; j >= 0; j--) {
            const b = bullets[j];
            if (checkCollision(b, e)) {
                bullets.splice(j, 1);
                e.hp--;

                if (e.hp <= 0) {
                    if (Math.random() < 0.35) {
                        items.push({
                            x: e.x,
                            y: e.y,
                            width: 20,
                            height: 20
                        });
                    }
                    score += (e.type === "boss") ? 30 : 10;
                    enemies.splice(i, 1);
                    break;
                }
            }
        }

        // 플레이어와 적 충돌
        if (enemies[i] && checkCollision(player, e)) {
            endGame();
            return;
        }

        // 화면 밖 적 제거
        if (enemies[i] && e.y - e.height / 2 > HEIGHT) {
            enemies.splice(i, 1);
        }
    }

    // 아이템 이동 및 습득
    for (let i = items.length - 1; i >= 0; i--) {
        const item = items[i];
        item.y += 3;

        if (checkCollision(player, item)) {
            items.splice(i, 1);
            powerUpTimer = 250;
        } else if (item.y > HEIGHT + 20) {
            items.splice(i, 1);
        }
    }

    // 적 스폰
    const spawnChance = 0.03 + (difficultyLevel * 0.008);
    if (Math.random() < Math.min(spawnChance, 0.12)) {
        spawnEnemy();
    }
}

function render() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    // 전체 폭탄 효과
    if (flashTimer > 0) {
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        flashTimer--;
        return;
    }

    // 플레이어 그리기 (삼각형)
    ctx.fillStyle = player.color;
    ctx.strokeStyle = "white";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(player.x, player.y - 20);
    ctx.lineTo(player.x - 20, player.y + 20);
    ctx.lineTo(player.x + 20, player.y + 20);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 아군 총알 그리기
    for (const b of bullets) {
        ctx.fillStyle = b.color;
        ctx.fillRect(b.x - b.width / 2, b.y - b.height / 2, b.width, b.height);
    }

    // 적 총알 그리기
    for (const eb of enemyBullets) {
        ctx.fillStyle = "red";
        ctx.strokeStyle = "orange";
        ctx.lineWidth = 1;
        ctx.fillRect(eb.x - eb.width / 2, eb.y - eb.height / 2, eb.width, eb.height);
        ctx.strokeRect(eb.x - eb.width / 2, eb.y - eb.height / 2, eb.width, eb.height);
    }

    // 적 그리기
    for (const e of enemies) {
        if (e.type === "boss") {
            ctx.fillStyle = "orange";
            ctx.strokeStyle = "red";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(e.x, e.y + 20);
            ctx.lineTo(e.x - 25, e.y - 20);
            ctx.lineTo(e.x + 25, e.y - 20);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        } else {
            ctx.fillStyle = "red";
            ctx.strokeStyle = "pink";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.ellipse(e.x, e.y, 18, 18, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }
    }

    // 파워업 아이템 그리기
    for (const item of items) {
        ctx.fillStyle = "lime";
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1;
        ctx.fillRect(item.x - 10, item.y - 10, 20, 20);
        ctx.strokeRect(item.x - 10, item.y - 10, 20, 20);
    }

    // UI 텍스트
    ctx.font = "bold 16px Arial";
    ctx.textAlign = "left";
    ctx.fillStyle = "white";
    ctx.fillText(`점수: ${score}`, 20, 30);

    ctx.textAlign = "center";
    ctx.fillStyle = "orange";
    ctx.fillText(`LVL: ${difficultyLevel}`, WIDTH / 2, 30);

    ctx.textAlign = "left";
    ctx.fillStyle = "yellow";
    ctx.font = "bold 14px Arial";
    ctx.fillText(`폭탄(B): 💣x${bombs}`, 20, HEIGHT - 20);

    if (powerUpTimer > 0) {
        ctx.textAlign = "right";
        ctx.fillStyle = "lime";
        ctx.fillText(`파워업! (${Math.floor(powerUpTimer / 50)}s)`, WIDTH - 20, HEIGHT - 20);
    }

    // 시작 안내 문구
    if (showIntro && !gameOver) {
        ctx.textAlign = "center";
        ctx.font = "bold 16px Arial";
        ctx.fillStyle = "white";
        ctx.fillText("← A / D → : 이동", WIDTH / 2, 280);
        ctx.fillStyle = "yellow";
        ctx.fillText("Spacebar : 총알 발사 / B : 전체 폭탄", WIDTH / 2, 310);
        ctx.fillStyle = "red";
        ctx.fillText("적의 총알과 적에 피격 시 즉시 사망!", WIDTH / 2, 340);
    }

    // 게임 오버 화면
    if (gameOver) {
        ctx.textAlign = "center";
        ctx.font = "bold 38px Arial";
        ctx.fillStyle = "red";
        ctx.fillText("GAME OVER", WIDTH / 2, HEIGHT / 2 - 40);

        ctx.font = "bold 22px Arial";
        ctx.fillStyle = "yellow";
        ctx.fillText(`최종 점수: ${score}`, WIDTH / 2, HEIGHT / 2 + 10);

        ctx.font = "bold 18px Arial";
        ctx.fillStyle = "orange";
        ctx.fillText(`도달 난이도: LVL ${difficultyLevel}`, WIDTH / 2, HEIGHT / 2 + 45);

        ctx.font = "15px Arial";
        ctx.fillStyle = "white";
        ctx.fillText("R 키를 눌러 다시 시작", WIDTH / 2, HEIGHT / 2 + 90);
    }
}

function loop() {
    update();
    render();
    requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
</script>
</body>
</html>