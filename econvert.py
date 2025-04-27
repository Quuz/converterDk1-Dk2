import struct
import numpy as np
from collections import deque

def convert_dk1_to_dk2_all_red(slb_path: str, output_path: str):
    """
    Упрощенный конвертер DK1 -> DK2:
    - base_slab по таблице conv_base
    - owner = 3 (красный) для всех
    - drape=0, flag=1
    - overlay сердце 5×5 (owner = 3)
    """
    # Загрузка .slb
    slb_raw = open(slb_path, "rb").read()
    total = len(slb_raw) // 2
    side = int(total ** 0.5)
    W = H = side

    # Парсинг slab_ids
    slabs = np.frombuffer(slb_raw, dtype="<H").reshape((H, W))

    # Таблица преобразования base_slab
    conv_base = {
        0:1,1:6,2:2,3:2,
        4:9,5:9,6:9,7:9,8:9,9:9,
        10:3,11:8,12:5,13:4,14:12,15:9,
        16:10,17:9,18:15,19:9,20:20,21:9,
        22:21,23:9,24:16,25:9,26:14,27:9,
        28:19,29:9,30:24,31:9,32:22,33:9,
        34:23,35:9,36:13,37:9,38:11,39:9,
        40:25,41:9,51:17,52:7,53:18
    }

    # Инициализация
    base = np.zeros((H, W), dtype=np.uint8)
    owner = np.full((H, W), 3, dtype=np.uint8)  # красный для всех
    drape = np.zeros((H, W), dtype=np.uint8)

    # Заполняем base и owner
    for y in range(H):
        for x in range(W):
            sid = int(slabs[y, x])
            base[y, x] = conv_base.get(sid, 1)

    # Накладываем сердце 5×5, owner = красный
    visited = np.zeros((H, W), dtype=bool)
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    for y in range(H):
        for x in range(W):
            if slabs[y, x] == 26 and not visited[y, x]:
                queue = deque([(y, x)])
                visited[y, x] = True
                cluster = [(y, x)]
                while queue:
                    cy, cx = queue.popleft()
                    for dy, dx in dirs:
                        ny, nx = cy+dy, cx+dx
                        if 0 <= ny < H and 0 <= nx < W and not visited[ny, nx] and slabs[ny, nx] == 26:
                            visited[ny, nx] = True
                            queue.append((ny, nx))
                            cluster.append((ny, nx))
                cy = int(round(sum(p[0] for p in cluster)/len(cluster)))
                cx = int(round(sum(p[1] for p in cluster)/len(cluster)))
                for yy in range(cy-2, cy+3):
                    for xx in range(cx-2, cx+3):
                        if 0 <= yy < H and 0 <= xx < W:
                            base[yy, xx] = 14
                            owner[yy, xx] = 3

    # Сборка заголовка .kld
    section_size = W * H * 4 + 36
    header = bytearray()
    for v in [100, 4, section_size, 101, 8, W, H, 102, section_size]:
        header += struct.pack("<I", v)

    # Пакет данных
    body = bytearray()
    for y in range(H):
        for x in range(W):
            body += bytes([base[y, x], owner[y, x], 1, drape[y, x]])

    # Запись
    with open(output_path, "wb") as f:
        f.write(header + body)

# Генерация файла для MAP00007
convert_dk1_to_dk2_all_red(
    slb_path=r"C:\Converter\map00015.SLB",
    output_path=r"C:\Converter\map00015.kld",
)

"/mnt/data/MAP00007_AllRed.kld"
