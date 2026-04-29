metadata name = 'Shared Type Definitions'
metadata description = 'Common types and defaults for intelligent matching infrastructure.'

/* =========================================================================
   DEPLOYMENT CONFIGURATION
   ========================================================================= */

@export()
@description('Common deployment configuration.')
type DeploymentConfig = {
  @description('Resource name prefix (e.g., company or project identifier).')
  resourcePrefix: string

  @description('Environment: dev, test, or prod.')
  environment: 'dev' | 'test' | 'prod'

  @description('Instance identifier for multi-deployment scenarios.')
  instance: string
}

@export()
@description('Default deployment configuration values.')
var deploymentDefaults = {
  resourcePrefix: 'wm'
  environment: 'dev'
  instance: '001'
}
