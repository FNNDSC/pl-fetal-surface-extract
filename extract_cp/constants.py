"""
Magic constants which set how many iterations should be performed by
internal subroutines. These values are primarily dependent on brain size,
and the specific values here are appropriate for fetal brain MRI inner CP
between 23-35 GA.
"""

# parameters for inflate_to_sphere_implicit
N_INFLATE = 200
N_SMOOTH = 200
