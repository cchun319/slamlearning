# SLAM ENGINEER
## Introduction
This is a living journey of me becoming a SLAM engineer. I will keep developing working examples, write-ups and visualization tools to help myself understanding things better. Feel free to let me know if I make any mistakes. 
## Roadmap

```mermaid
graph TD
    A[Pose Graph Optimization] --> C
    B1[ICP-point] --> B
    B2[ICP-plane] --> B
    B3[GICP] --> B
    B[ICP]
    C[Visual SLAM]
    F1[Direct Method] --> F
    F2[Feature Method] --> F 
    F21[Descriptor] --> F2
    F3[Nearest Neighbor] --> F2
    F[Visual Odometry]
    D[Lidar SLAM]
    E[Kalman Variants]
    G[Wheel Odometry]
    A --> D
    B --> D
    G --> C
    G --> D
    F --> C
    H[Lie Algebra] --> A
    I[Newton Method & Variants, LM] --> A
    J[Outlier Rejection]
    J --> F1
    J --> F2
    J --> B1
    J --> B2
    J --> B3
    K[Hypothesis Testing] --> J
    L[Pose Error Representation] --> H
    L1[Rotation Representation] --> L

```

## reference