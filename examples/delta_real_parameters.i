[Mesh]
  file=07-heart_geometry_new.e
  block_id='1'
  block_name='all'
  displacements='dispx dispy dispz'
  # uniform_refine=1
[]

[Variables]
  [./dispx] order=FIRST family=LAGRANGE [../]
  [./dispy] order=FIRST family=LAGRANGE [../]
  [./dispz] order=FIRST family=LAGRANGE [../]

  [./hydrostatic_pressure] order=FIRST family=SCALAR [../]
[]

[Kernels]
  [./stressdiv_dispx] type=CardiacKirchhoffStressDivergence  variable=dispx  component=0  displacements='dispx dispy dispz' [../]
  [./stressdiv_dispy] type=CardiacKirchhoffStressDivergence  variable=dispy  component=1  displacements='dispx dispy dispz' [../]
  [./stressdiv_dispz] type=CardiacKirchhoffStressDivergence  variable=dispz  component=2  displacements='dispx dispy dispz' [../]

  #[./inertia_x] type=SecondOrderImplicitEulerWithDensity  variable=dispx  density=0.0  lumping=false [../]
  #[./inertia_y] type=SecondOrderImplicitEulerWithDensity  variable=dispy  density=0.0  lumping=false [../]
  #[./inertia_z] type=SecondOrderImplicitEulerWithDensity  variable=dispz  density=0.0  lumping=false [../]
[]

[ScalarKernels]
  [./incompressibility] type=CardiacIncompressibilityLagrangeMultiplier  variable=hydrostatic_pressure  volume_ratio_postprocessor=volume_ratio [../]
[]

[AuxVariables]
  [./distance_outer]      order=FIRST family=LAGRANGE [../]
  [./distance_RV_inner]   order=FIRST family=LAGRANGE [../]
  [./distance_LV_inner]   order=FIRST family=LAGRANGE [../]
  [./thickness_parameter] order=FIRST family=LAGRANGE [../]
  [./potential_from_sub]  order=FIRST family=LAGRANGE [../]
  [./active_tension]      order=CONSTANT family=MONOMIAL [../]
[]

[AuxKernels]
  [./auxdistance_outer]    type=VolumeNearestNodeDistanceAux  variable=distance_outer     block=all  paired_boundary=ss_outer    [../]
  [./auxdistance_RV_inner] type=VolumeNearestNodeDistanceAux  variable=distance_RV_inner  block=all  paired_boundary=ss_RV_inner [../]
  [./auxdistance_LV_inner] type=VolumeNearestNodeDistanceAux  variable=distance_LV_inner  block=all  paired_boundary=ss_LV_inner [../]

  [./auxthickness]
    type=CardiacThicknessParameterAux variable=thickness_parameter
    distance_RV_inner=distance_RV_inner
    distance_LV_inner=distance_LV_inner
    distance_outer   =distance_outer
  [../]

 [./aux_active_tension]  type=MaterialRealAux property=active_tension variable=active_tension [../]
[]

[Materials]
  [./fibres]
    type=CardiacFibresMaterial
    block=all
    thickness_parameter=thickness_parameter
    #fixed_R='0.36 0.48 -0.8 -0.8 0.6 0.0 0.48 0.64 0.60'
    #fixed_R='0 0 1 1 0 0 0 1 0'
    outputs=all
  [../]

  [./cardiac_material]
    type=CardiacHolzapfel2009Material
    block=all
    use_displaced_mesh=false
    # material parameters as given in Table 1 of [Holzapfel 2009]
    #in following order:     a,    b,   a_f,   b_f,  a_s,   b_s, a_fs,  b_fs
    material_parameters='0.059 8.023 18.472 16.026 2.481 11.120 0.216 11.436'
    displacements ='dispx dispy dispz'
    outputs=all
    output_properties='Kirchhoff_stress'
    Ta=active_tension
    p=hydrostatic_pressure
  [../]

  [./active_tension_material]
    type=ActiveTensionODE
    Vmem=potential_from_sub
    block=all
    # these are the default parameter values, including them here to make sure they are not forgotten as tunable options
    epsilon_recovery=0.01
    epsilon_development=0.04
    kTa=47.9
    Vrest=-90.272
    Vmax=0.
  [../]
[]

[BCs]
  [./dispx_fixed] type=DirichletBC  variable=dispx  boundary='ss_apex'  value=0 [../]
  [./dispy_fixed] type=DirichletBC  variable=dispy  boundary='ss_apex'  value=0 [../]
  [./dispz_fixed] type=DirichletBC  variable=dispz  boundary='ss_apex'  value=0 [../]

#  [./ns_lower_polar_point_x] type=DirichletBC  variable=dispx  boundary=ns_lower_polar_point  value=0 [../]
#  [./ns_lower_polar_point_y] type=DirichletBC  variable=dispy  boundary=ns_lower_polar_point  value=0 [../]
#  [./ns_lower_polar_point_z] type=DirichletBC  variable=dispz  boundary=ns_lower_polar_point  value=0 [../]
#  [./ns_lower_polar_neighbour_x] type=DirichletBC  variable=dispx  boundary=ns_lower_polar_neighbour  value=0 [../]
#  [./ns_lower_polar_neighbour_y] type=DirichletBC  variable=dispy  boundary=ns_lower_polar_neighbour  value=0 [../]
#  [./ns_lower_polar_neighbour_z] type=DirichletBC  variable=dispz  boundary=ns_lower_polar_neighbour  value=0 [../]
#  [./ring_x] type=DirichletBC  variable=dispx  value=0  boundary=ns_LV_opening [../]
#  [./ring_y] type=DirichletBC  variable=dispy  value=0  boundary=ns_LV_opening [../]
#  [./ring_z] type=DirichletBC  variable=dispz  value=0  boundary=ns_LV_opening [../]
[]

[Postprocessors]
  #[./elastic_energy] type=ElementIntegralMaterialProperty execute_on=timestep mat_prop=elastic_energy_density [../]
  [./volume_ratio] type=CardiacMaterialVolumeRatioPostprocessor execute_on=residual [../]
[]

[Executioner]
  type=Transient

  solve_type=PJFNK
  splitting = 'saddlepoint_fieldsplit'
  petsc_options='-fp_trap -info -snes_monitor -snes_converged_reason -ksp_monitor -ksp_converged_reason  -ksp_monitor_true_residual -pc_svd_monitor'

  nl_rel_tol=1e-5
  nl_abs_tol=1e-5
  nl_rel_step_tol=1e-6
  nl_abs_step_tol=1e-6

  l_tol=1.e-8
  l_max_its=30
  #l_abs_step_tol=1.e-12
  #l_max_its=20

  #line_search=default  # TODO: what else?

  start_time=0
  end_time  =500.0
  dtmin     =0.025
  dtmax     =0.5
[]

[Splits]
  [./saddlepoint_fieldsplit]
    splitting = 'disp pressure'
    splitting_type  = schur
    schur_type    = full
    schur_pre     = S
    petsc_options = '-dm_view'
  [../]
  [./disp]
    vars = 'dispx dispy dispz'
    petsc_options = '-dm_view'
    petsc_options_iname = '-pc_type -pc_hypre_type -pc_hypre_boomeramg_max_iter'
    petsc_options_value = '   hypre  boomeramg      8                          '
  [../]
  [./pressure]
    vars = 'hydrostatic_pressure'
    petsc_options = '-dm_view'
    petsc_options_iname = '-pc_type'
    petsc_options_value = '    none'
  [../]
[]

[Outputs]
  [./console]
    type=Console
    perf_log=true
    linear_residuals=true
  [../]
  
  [./exodus_displaced]
     type=Exodus
  [../]
[]

[MultiApps]
  [./electrocardio]
    type=TransientMultiApp
    app_type=EweApp
    execute_on=timestep_begin
    input_files=delta_real_parameters_sub.i
    positions='0.0 0.0 0.0'
  [../]
[]

[Transfers]
  [./dispx_to_sub]
    type=MultiAppNearestNodeTransfer
    direction=to_multiapp
    execute_on=timestep_begin
    multi_app=electrocardio
    source_variable=dispx
    variable=dispx
    fixed_meshes=true # independent of any deformation we want to make sure that transfer always happens between the same node pairs
  [../]
  [./dispy_to_sub]
    type=MultiAppNearestNodeTransfer
    direction=to_multiapp
    execute_on=timestep_begin
    multi_app=electrocardio
    source_variable=dispy
    variable=dispy
    fixed_meshes=true # independent of any deformation we want to make sure that transfer always happens between the same node pairs
  [../]
  [./dispz_to_sub]
    type=MultiAppNearestNodeTransfer
    direction=to_multiapp
    execute_on=timestep_begin
    multi_app=electrocardio
    source_variable=dispz
    variable=dispz
    fixed_meshes=true # independent of any deformation we want to make sure that transfer always happens between the same node pairs
  [../]
  [./from_sub]
    type=MultiAppNearestNodeTransfer
    direction=from_multiapp
    execute_on=timestep_begin
    multi_app=electrocardio
    source_variable=potential
    variable=potential_from_sub
    fixed_meshes=true # independent of any deformation we want to make sure that transfer always happens between the same node pairs
  [../]
[]