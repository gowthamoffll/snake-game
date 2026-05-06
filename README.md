# Pygame Snake (Nokia Aesthetic)

A modern take on the classic Snake game, emphasizing visual polish and a retro "greenscreen" color palette. This implementation features smooth body rendering, animated sprites (like the flicking tongue and pulsing apple), and a wrap-around game world.

## 🟢 Features
*   **Retro Visuals:** Custom-built color palette inspired by classic handheld displays.
*   **Polished Graphics:** Includes a pulsing apple animation, a flickering snake tongue, and a "death flash" effect upon losing.
*   **Wrap-Around Grid:** The snake can pass through walls and reappear on the opposite side.
*   **Dynamic HUD:** Real-time score tracking and a persistent high-score system.
*   **Clean Geometry:** Procedural rendering of snake segments for a connected, organic look.

## 🎮 Controls
*   **Arrow Keys:** Change snake direction.
*   **Space / Enter:** Start game or restart after Game Over.
*   **Escape:** Exit to the main menu.

## 🛠️ Requirements
*   Python 3.x
*   Pygame library

## 🚀 How to Run
1.  **Install Pygame** (if you haven't already):
    ```bash
    pip install pygame
    ```
2.  **Run the script**:
    ```bash
    python snake.py
    ```

## 📐 Layout Constants
*   **Grid Size:** 25x25 cells
*   **Cell Size:** 24 pixels
*   **FPS:** 10 (Classic arcade speed)

## 🎨 Color Palette Reference
The game uses a tiered green system:
*   **Background:** `(10, 20, 10)`
*   **Snake Head:** `(80, 230, 80)`
*   **Apple:** `(220, 50, 40)`
```