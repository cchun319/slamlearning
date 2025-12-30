# Lie Algebra


##
se3 is locally flat and SE3 is globally curved so addition doesn't stay in SE3
##
$$ \text{twist vector } se3: \xi = \begin{pmatrix} \rho \\ \phi \end{pmatrix} \in \mathbb{R}^6\xrightleftarrows[{\vee}]{skew}  \xi^{\wedge} \xrightleftarrows[{log}]{exp} \text{lie group}: \underset{4 \times 4}{T} \in SE3$$

$$exp(\xi^{\wedge}) = 
\begin{bmatrix} 
exp(\phi^{\wedge}) & V(\phi)\rho \\
0 & 1
\end{bmatrix}$$

