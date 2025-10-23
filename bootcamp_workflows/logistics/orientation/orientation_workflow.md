---
name: Orientation Workflow
description: First-time onboarding for bootcamp participants - sets up workspace and gets to know them
initial_state: workspace_setup
states:
  workspace_setup:
    description: |
      Goal: Create complete folder structure for bootcamp participant workspace
      Input: Current directory (should be where your_workspace/ will be created)
      Output: Full your_workspace/ folder structure with logs initialized, profile/reports/data/your_workflows folders created
    prompt_file: "step1_workspace_setup_prompt.txt"
    on_success: profile_conversation

  profile_conversation:
    description: |
      Goal: Have natural conversation to understand who the participant is and what they're hoping to achieve
      Input: Conversational discovery (no forms!)
      Output: participant_profile.md with natural, conversational content about their background and objectives
    prompt_file: "step2_profile_conversation_prompt.txt"
    on_success: goal_setting

  goal_setting:
    description: |
      Goal: Help participant set realistic personal goals for the bootcamp
      Input: Their profile information, bootcamp structure
      Output: Personal goals added to participant_profile.md
    prompt_file: "step3_goal_setting_prompt.txt"
    on_success: project_ideation

  project_ideation:
    description: |
      Goal: Help participant identify and document their project idea for sharing with mentors and potential teammates
      Input: Their profile, interests, background; optionally review prior bootcamp demos
      Output: Project idea documented in profile (either specific idea or shortlist of 3 options)
    prompt_file: "step4_project_ideation_prompt.txt"
    on_success: finalize_setup

  finalize_setup:
    description: |
      Goal: Complete setup by creating lock file and welcome message
      Input: All setup complete, profile created, goals set, project documented
      Output: .workflow_initialized lock file created, welcome message, return to master orchestration
    prompt_file: "step5_finalize_setup_prompt.txt"
    on_success: done

  done:
    description: "Orientation complete. Participant ready to use master orchestration workflow."
---
