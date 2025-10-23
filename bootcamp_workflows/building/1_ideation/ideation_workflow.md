---
name: AI Agent Ideation Workflow
description: A guided workflow for identifying automation opportunities and designing semi-autonomous AI workflows
initial_state: step1_problem_framing
states:
  step1_problem_framing:
    description: |
      Goal: Define the workflow inefficiency or repetitive task that could benefit from AI autonomy.
      Input: User's initial description of a time-consuming or repetitive workflow.
      Output: A structured problem document with clear scope, current process, and success metrics.
    prompt_file: "step1_problem_framing_prompt.txt"
    on_success: step2_assumption_challenging

  step2_assumption_challenging:
    description: |
      Goal: Identify and test assumptions about the workflow and constraints.
      Input: The problem definition from Step 1.
      Output: A list of validated assumptions and beliefs that need testing.
    prompt_file: "step2_assumption_challenging_prompt.txt"
    on_success: step3_solution_generation

  step3_solution_generation:
    description: |
      Goal: Generate multiple distinct approaches to add autonomy to the workflow.
      Input: Problem definition and validated assumptions.
      Output: 3+ different solution approaches with varying levels of human-in-the-loop interaction.
    prompt_file: "step3_solution_generation_prompt.txt"
    on_success: step4_solution_selection

  step4_solution_selection:
    description: |
      Goal: Select the most promising solution and define its autonomous capabilities.
      Input: List of solution approaches.
      Output: A chosen solution with clear definition of agent autonomy, human touchpoints, and expected outcomes.
    prompt_file: "step4_solution_selection_prompt.txt"
    on_success: step5_experiment_design

  step5_experiment_design:
    description: |
      Goal: Design a simple test to validate the autonomous workflow concept.
      Input: The chosen solution design.
      Output: A concrete experiment plan with success metrics.
    prompt_file: "step5_experiment_design_prompt.txt"
    on_success: step6_workflow_generation

  step6_workflow_generation:
    description: |
      Goal: Generate a YAML workflow structure and prompt files that implement the solution.
      Input: The validated solution design and experiment plan.
      Output: A complete workflow package (YAML + prompt files) ready to use in any LLM CLI or chat interface.
    prompt_file: "step6_workflow_generation_prompt.txt"
    on_success: done

  done:
    description: "The ideation session is complete. You now have a validated workflow ready to implement."
---
