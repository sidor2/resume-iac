# cloud-resume-challenge

The [Cloud Resume Challenge](https://cloudresumechallenge.dev/docs/the-challenge/aws/) was created by [Forrest Brazeal](https://forrestbrazeal.com/) as a self-guided, hands-on project to incorporate a large range of skills used by DevOps Engineers and Cloud Developers.

The challenge is designed to champion *self-learning* as it intentionally gives only high-level guidance on how to research, navigate, and implement core topics such as DNS, APIs, Testing, Infrastructure-as-Code, and CI/CD pipelines.

</br>

My website is built on AWS using S3, CloudFront, Route 53, Certificate Manager, Lambda, DynamoDB, API Gateway, and the Boto3 Python SDK.

Infrastructure-as-Code is implemented using AWS Python CDK, while two CI/CD pipelines are triggered and executed using GitHub Actions. Although the challenge asks for utilizing Terraform, I was already in the process of learning the CDK and decided to 

</br>

View the site at [**www.sidor.com**](https://www.sidor.com).

Check out my article about completing the project here:  [**The Cloud Resume Challenge:  My DevOps Journey from Building Technology to the Cloud**](https://www.linkedin.com/pulse/cloud-resume-challenge-my-devops-journey-from-building-william-lewis)


<img src="./website-architecture-diagram.svg" alt="Website Architecture Diagram" width="100%" height="56.25%">

</br>
</br>

---

## Challenge Steps & Notes:


- [x]  1. Earn an **AWS Certification**
    - AWS Certified Solutions Architect – Associate, September 2022
    - AWS Certified Security – Specialty, March 2023

- [ ]  2. Write Resume in **HTML**
    - 
    - 

- [ ]  3. Style Resume in **CSS**
    - 

- [ ]  4. Deploy Resume to Static Website with **AWS S3**
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

- [ ] 11. Perform **Tests** on Python Code
    - tests run using `pytest` and `moto` frameworks for lambda testing locally
    - `pytest` framework is used for testing CloudFormation template synthesis

- [ ] 12. Configure Resources with **IaC**
    - 

- [ ] 13. Utilize **Source Control** with GitHub
    - 

- [ ] 14. Implement **Backend CI/CD** with GitHub Actions
    - 

- [ ] 15. Implement **Frontend CI/CD** for Webpage Content with GitHub Actions
    - 

- [ ] 16. Share Your Challenges and Learnings with a **Blog Post**
    - article published on LinkedIn

