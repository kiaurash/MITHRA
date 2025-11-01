---
name: Master Orchestration Workflow
description: Adaptive coaching and navigation system for bootcamp participants
initial_state: check_initialization
states:
  check_initialization:
    description: |
      Goal: Determine if participant has completed orientation
      Input: Check for existence of bootcamp2510/.workflow_initialized lock file
      Output: Route to orientation_redirect if lock doesn't exist, or progress_assessment if it does
    prompt_file: "step1_check_initialization_prompt.txt"
    on_success: progress_assessment

  orientation_redirect:
    description: |
      Goal: Redirect first-time participant to orientation workflow
      Input: No lock file exists
      Output: Welcome message and automatic launch of orientation workflow
    prompt_file: "step2_orientation_redirect_prompt.txt"
    on_success: progress_assessment

  progress_assessment:
    description: |
      Goal: Show participant where they are in the bootcamp journey with visual progress indicators
      Input: Current date, cohort start date (Oct 20, 2025), activity_log.csv, participant goals
      Output: ASCII visualization of progress, sprint status, upcoming deadlines, comparison to personal goals
    prompt_file: "step3_progress_assessment_prompt.txt"
    on_success: menu_and_routing

  menu_and_routing:
    description: |
      Goal: Present menu of available workflows and route participant to their chosen workflow
      Input: Participant's current status, available logistics and building workflows
      Output: Route to selected logistics prompt, building workflow placeholder, or exit gracefully
    prompt_file: "step4_menu_and_routing_prompt.txt"
    on_success: done

  done:
    description: "Master orchestration workflow complete. Participant has been routed to their chosen next step."
---
