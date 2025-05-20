# Datum Knowledge Base Highlights for Engineering

## Deploying IAM System (aka Milo) specific branch to staging

To deploy a specific branch of the IAM System (aka Milo) to the staging environment, replace [this line](https://github.com/datum-cloud/datum-infra/blob/deploy-datum-iam-system/apps/datum-iam-system/staging/patches/iam-apiserver-image-updater.yaml#L25):

```yaml
spec:
  filterTags:
    pattern: 'feature-subject-parent-resolution-.*'
```

with the name of the branch you wish to deploy. This will automatically deploy the IAM System (aka Milo) to the staging environment.


## Deploying Cloud Portal specific branch to staging

To deploy a specific branch of the Cloud Portal to the staging environment, replace [this line](https://github.com/datum-cloud/datum-infra/blob/deploy-datum-iam-system/apps/cloud-portal/staging/image-updater.yaml#L17):

```yaml
spec:
  filterTags:
    pattern: 'main-.*'
```

with the name of the branch you wish to deploy. This will automatically deploy the Cloud Portal to the staging environment.
