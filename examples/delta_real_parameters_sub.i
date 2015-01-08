[Mesh]
  file = 07-heart_geometry_new.e
  block_id = '1'
  block_name = 'all'
  displacements = 'dispx dispy dispz'
  # uniform_refine = 1
[]

[Variables]
  [./potential] order = FIRST family = LAGRANGE [../]
[]

[AuxVariables]
  [./gate_m]  order = CONSTANT family = MONOMIAL [../]
  [./gate_v]  order = CONSTANT family = MONOMIAL [../]
  [./gate_f]  order = CONSTANT family = MONOMIAL [../]
  [./gate_to] order = CONSTANT family = MONOMIAL [../]
  [./gate_x]  order = CONSTANT family = MONOMIAL [../]
  [./dispx]   order = FIRST    family = LAGRANGE [../]
  [./dispy]   order = FIRST    family = LAGRANGE [../]
  [./dispz]   order = FIRST    family = LAGRANGE [../]
  #
  [./distance_outer]      order=FIRST family=LAGRANGE [../]
  [./distance_RV_inner]   order=FIRST family=LAGRANGE [../]
  [./distance_LV_inner]   order=FIRST family=LAGRANGE [../]
  [./thickness_parameter] order=FIRST family=LAGRANGE [../]
[]

[AuxKernels]
  [./auxgate_m]  type = MaterialStdVectorAux property = 'gates' variable = gate_m  block = all index = 0 [../]
  [./auxgate_v]  type = MaterialStdVectorAux property = 'gates' variable = gate_v  block = all index = 1 [../]
  [./auxgate_f]  type = MaterialStdVectorAux property = 'gates' variable = gate_f  block = all index = 2 [../]
  [./auxgate_to] type = MaterialStdVectorAux property = 'gates' variable = gate_to block = all index = 3 [../]
  [./auxgate_x]  type = MaterialStdVectorAux property = 'gates' variable = gate_x  block = all index = 4 [../]
  #
  [./auxdistance_outer]    type=VolumeNearestNodeDistanceAux  variable=distance_outer     block=all  paired_boundary=ss_outer    [../]
  [./auxdistance_RV_inner] type=VolumeNearestNodeDistanceAux  variable=distance_RV_inner  block=all  paired_boundary=ss_RV_inner [../]
  [./auxdistance_LV_inner] type=VolumeNearestNodeDistanceAux  variable=distance_LV_inner  block=all  paired_boundary=ss_LV_inner [../]

  [./auxthickness]
    type=CardiacThicknessParameterAux variable=thickness_parameter
    distance_RV_inner=distance_RV_inner
    distance_LV_inner=distance_LV_inner
    distance_outer   =distance_outer
  [../]
[]

[Kernels]
  [./diff]
    type = ElectrocardioDiffusion
    variable = potential
    surface_to_volume = 1000.0
    capacitance = 1.0
    use_displaced_mesh = true
  [../]
  
  [./ecforcing]
    type = ElectrocardioForcing
    variable = potential
    forcing_function = ElectrocardioForcing_function
    #ion_coeff = 0.0
    use_displaced_mesh = true
  [../]

  [./euler]
    type = ElectrocardioTimeDerivative
    variable = potential
    use_displaced_mesh = true
  [../]
[]

[Functions]
  [./ElectrocardioForcing_function]
    # we are pacing at the following "early activation sites" which were hand-picked in Paraview
    # to closely match [Potse2006, Figure 1]:
    #   0.8 6.4 -3.1
    #  -1.4 6.4 -2.9
    #   2.2 8.9 -4.2
    type = PiecewiseParsedFunction
    default_function = '0'
    functions = '-30.0*exp(-0.5*pow(x-0.8,2.0)/pow(0.15,2.0)-0.5*pow(y-6.4,2.0)/pow(0.15,2.0)-0.5*pow(z+3.1,2.0)/pow(0.15,2.0))+-30.0*exp(-0.5*pow(x+1.4,2.0)/pow(0.15,2.0)-0.5*pow(y-6.4,2.0)/pow(0.15,2.0)-0.5*pow(z+2.9,2.0)/pow(0.15,2.0))+-30.0*exp(-0.5*pow(x-2.2,2.0)/pow(0.15,2.0)-0.5*pow(y-8.9,2.0)/pow(0.15,2.0)-0.5*pow(z+4.2,2.0)/pow(0.15,2.0))'
    left      = ' 0.0'
    right     = ' 5.0'
  [../]
[]

[BCs]
  [./bc]
    type = NeumannBC
    variable = potential
    boundary = 'ss_LV_inner ss_RV_inner ss_outer'
    value = 0
  [../]
[]

[Materials]
 [./cardiac_properties]
    type = CardiacFibresMaterial
    block = all
    thickness_parameter=thickness_parameter
    #fixed_R='0.36 0.48 -0.8 -0.8 0.6 0.0 0.48 0.64 0.60'
    #fixed_R='0 0 1 1 0 0 0 1 0'
    outputs = all
  [../]
  
  [./electrocardio]
    type = Electrocardio
    vmem = 'potential'
    block = all
    outputs = all
    #use_displaced_mesh = true # TODO: if activated I am getting a segfault
  [../]
 
  [./conductivity]
    type = ElectrocardioConductivity
    conductivities = '0.0012 0.003 0.003'
    block = all
    #use_displaced_mesh = true # TODO: if activated I am getting a segfault
  [../]
[]

[Executioner]
  type = Transient   # Here we use the Transient Executioner
  #Preconditioned JFNK (default)
  solve_type = 'PJFNK'
#l_tol = 1e-6
#  l_max_its = 10
  nl_rel_tol = 1e-3
  nl_abs_tol = 1e-6
  nl_rel_step_tol = 1e-6
  nl_max_its = 2

  start_time = 0
  end_time   = 500.0
  dtmin = 0.05
  dtmax = 0.5
  scheme = 'implicit-euler'
[]

[ICs]
  [./ec]
    type = ElectrocardioIC
    variable = potential
    block = all
  [../]
[]
 
[Outputs]
  #exodus = true
  [./console]
    type = Console
    perf_log = false
    linear_residuals = false
  [../]
[]
