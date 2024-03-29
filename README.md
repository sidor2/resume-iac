# Cloud Resume Challenge
[Forrest Brazeal](https://forrestbrazeal.com/) developed the [Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/aws/) as an independent and interactive undertaking aimed at integrating a diverse set of skills employed by DevOps Engineers and Cloud Developers.

The objective of this challenge is to emphasize the importance of self-directed learning by providing limited instructions regarding researching, navigating, and implementing fundamental subjects like DNS, APIs, Testing, Infrastructure-as-Code, and CI/CD pipelines.

</br>

My website is built on AWS using S3, CloudFront, Route 53, Certificate Manager, Lambda, DynamoDB, API Gateway, and the Boto3 Python SDK.

Infrastructure-as-Code is implemented using AWS Python CDK, and two CI/CD pipelines are triggered and executed using GitHub Actions. Although the challenge requires the use of Terraform, I had already begun learning AWS Python CDK. Therefore, I decided to leverage the opportunity of building the Cloud Resume Challenge infrastructure to enhance my knowledge of AWS CDK.

</br>

View the site at [**www.sidor.me**](https://www.sidor.me).


### Workflow Diagram
<img src="./CRCWorkflow.png" alt="Workflow diagram" width="75%" height="50%">

#### Stack Architecture Diagram
<img src="./diagram.png" alt="CDK App Architecture Diagram" width="50%" height="25%">

</br>
</br>

---

## Challenge Steps & Notes:

- [x]  1. Earn an **AWS Certification**
    - AWS Certified Solutions Architect – Associate, September 2022
    - AWS Certified Security – Specialty, March 2023

- [x]  2. Write Resume in **HTML**
    - used a free Bootstrap template

- [x]  3. Style Resume in **CSS**
    - added styles for displaying certificates and visitors counter

- [x]  4. Deploy Resume to Static Website with **AWS S3**
    - the S3 bucket is configured as the first origin and exposed via Cloudfront
    - public access is restricted only via the Cloudfront distribution by utilized OAC (origin access control)
    - Block Public Access is ON & static website feature disabled for compatibility with OAC

- [x]  5. Use HTTPS Protocol with **AWS CloudFront**
    - redirects any HTTP requests to HTTPS
    - uses AWS issued SSL certificate 
    - the bucket's resource policy is configured to enforce TLS
    - security headers configured for the distribution

- [x]  6. Point Custom DNS Domain Name with **AWS Route 53**
    - custom domain purchased through **Route 53**
    - a CNAME record points the domain name to Cloudfront distribution

- [x]  7. Create a Webpage Visitor Counter with **JavaScript**
    - on loading the website, GET request sent to the API to retrieve the updated counter value
    - latest number of page views displayed to visitor at page bottom

- [x]  8. Create a Visitor Counter Database with **AWS DynamoDB**
    - a table holds single record with single attribute which is updated by Lambda function

- [x]  9. Do Not Communicate Directly With **DynamoDB**
    - REST API configured as the second origin for the Cloudfront distribution, allowing for GET request
    - REST API can be invoked only via the Cloudfront distribution and proxies the API call to a Lambda function 
    - on website loading, API call is made, Lambda function is invoked
    - function checks latest count from table, increments by 1, and writes back to the table
    - the updated counter value is returned in JSON body

- [x] 10. Perform **Tests** on Python Code
    - tests run using `pytest` and `moto` frameworks for lambda testing locally
    - `pytest` framework is used for testing CloudFormation template synthesis

- [x] 11. Configure Resources with **IaC**
    - IaC configured using AWS Python CDK
    - The app contains 2 stacks:
        - Frontend infrastructure, S3WebsiteStack
        - Backend infrastructure, ApiGwDdbStack

- [x] 12. Utilize **Source Control** with GitHub
    - all code related to infrastructure stored in a GitHub repository
    - version control utilized to track changes and capture development over time

- [x] 13. Implement **Backend CI/CD** with GitHub Actions
    - workflows are triggered by a `push` event, or manually by `workflow_dispatch`
    - workflow runs on GitHub-hosted Linux runner
    - Python dependencies installed on runner per requirements.txt file using pip
    - GitHub Actions configured as trusted identity provider with AWS, utilizing OpenID Connect token-based authentication for short-lived credentials
    - ARN of GitHub Actions IAM Role passed into workflow file as an environmental variable using GitHub repository secrets

- [x] 14. Implement **Frontend CI/CD** for Webpage Content with GitHub Actions
    - a workflow is defined to trigger on push event
    - GitHub repo is synchronized to the S3 bucket
    - CloudFront caching is disabled while in development
    - invalidation script will be created after the release

- [ ] 15. Share Your Challenges and Learnings with a **Blog Post**
