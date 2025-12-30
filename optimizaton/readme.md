# pose optimization

## error function
$$\mathbb{E(r_{0:t})} = \sum{||r_i||_2} = \sum(r_{i}^T * Q_i  * r_i)
\\\\[10pt]\text{where $r_i$ is the residual at the time, $Q_i$ is the corresponding covariance. } r_i = \begin{bmatrix}
t_i \\
\phi_i 
\end{bmatrix} \in \mathbb{R}^6
$$

## factors
1. gps
2. Visual odometry

### unary factor

### between factor

$$ r = Z_{ij}T_{i}^{-1}T_{j}
\\\\[10pt] 
T_{ij} = 
\begin{bmatrix}
R_{ij} & R_{i}^{-1}(t_j - t_i) \\
0 & 1 
\end{bmatrix}$$

$Z$ is the obeservation from sensor. ex, the wheel encoder tells how much movements between two poses