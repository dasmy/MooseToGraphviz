[Mesh]
  file = two_squares.e
  dim = 2
[]

[Variables]
  [./u]
    initial_condition = 0.01
  [../]
[]

[Kernels]
  [./diff]
    type = ExampleDiffusion
    variable = u
  [../]
  [./td]
    type = TimeDerivative
    variable = u
  [../]
[]

[BCs]
  [./left]
    type = DirichletBC
    variable = u
    boundary = leftleft
    value = 0
  [../]
  [./right]
    type = DirichletBC
    variable = u
    boundary = rightright
    value = 1
  [../]
[]

[Materials]
  [./badm]
    type = BlockAverageDiffusionMaterial
    block = 'left right'
    block_average_userobject = bav
  [../]
[]

[UserObjects]
  [./bav]
    type = BlockAverageValue
    variable = u
    execute_on = timestep_begin
  [../]
[]

[Executioner]
  type = Transient
  num_steps = 10
  dt = 1

  #Preconditioned JFNK (default)
  solve_type = 'PJFNK'

  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  exodus = true
  output_on = 'initial timestep_end'
  [./console]
    type = Console
    perf_log = true
    output_on = 'timestep_end failed nonlinear linear'
  [../]
[]
