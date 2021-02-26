const output = `
#### Terragrunt Initialization \`${{ steps.plan_dev.outputs.init_outcome }}\`
#### Terragrunt Plan \`${{ steps.plan_dev.plan_outcome }}\`
<details><summary>Show Plan</summary>

\`\`\` terraform
"terragrunt\n${{ steps.plan_dev.outputs.plan_output }}"
\`\`\`

</details>
Pusher: @${{ github.actor }}`;

github.issues.createComment({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  body: output
})
