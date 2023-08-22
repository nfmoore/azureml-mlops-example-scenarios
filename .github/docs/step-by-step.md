# Step-by-Step Setup

> **Note**:
> The purpose of this section is to describe the steps required to set up all parts of this example scenario.

## Prerequisites

Before implementing this example scenario the following is needed:

- Azure subscription (contributor or owner)
- GitHub account

## 1. Initial Setup

> **Note**:
> As with all Azure Deployments, this will incur associated costs. Remember to teardown all related resources after use to avoid unnecessary costs.

> **Estimated setup time:**
> - Azure resource deployments: 20 minutes
> - Configure GitHub environments and secrets: 5 minutes
> - Run all GitHub workflows: 90 minutes

### 1.1. Deploy Azure Resources

You will need to create a resource group for resources associated with **`Staging`** and **`Production`** environments. The same or separate resource groups can be used.

Once these have been created a service principal must be created with a **`contributor`** role assigned to each resource group.

> **Note**: The aim of this demo is to setup a simple proof-of-concept, therefore a single resource group is used. If separate resources groups are required, the following instructions/steps will need adjustment to reflect this.

![1](./images/setup/01.png)
![2](./images/setup/02.png)
![3](./images/setup/03.png)
![4](./images/setup/04.png)
![5](./images/setup/05.png)
![6](./images/setup/06.png)
![7](./images/setup/07.png)
![8](./images/setup/08.png)
![9](./images/setup/09.png)
![10](./images/setup/10.png)
![11](./images/setup/11.png)
![12](./images/setup/12.png)
![13](./images/setup/13.png)
![14](./images/setup/14.png)
![15](./images/setup/15.png)
![16](./images/setup/16.png)
![17](./images/setup/17.png)
![18](./images/setup/18.png)
![19](./images/setup/19.png)
![20](./images/setup/20.png)
![21](./images/setup/21.png)
![22](./images/setup/22.png)
![23](./images/setup/23.png)
![24](./images/setup/24.png)
![25](./images/setup/25.png)
![26](./images/setup/26.png)
![27](./images/setup/27.png)
![28](./images/setup/28.png)
![29](./images/setup/29.png)
