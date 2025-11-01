# AI Agent Ideation Workflow (Bootcamp Edition)

## Purpose
This workflow guides you through identifying workflow inefficiencies in your personal or business processes and designing semi-autonomous AI agent solutions. It's specifically designed for participants in the AI Agents Bootcamp who want to add autonomy to repetitive tasks.

By the end of this workflow, you'll have:
- A clearly defined workflow problem
- A validated solution approach
- An experiment plan to test your solution
- **A complete, executable workflow** (YAML + prompt files) ready to use in any LLM interface

## What Makes This Different
Most problem-solving approaches stop at planning. This workflow goes further:
- **Step 6 teaches you to build workflows** that can be executed by LLMs
- You'll learn to create **reusable autonomous workflows** for any problem
- The workflow generates its own "children"—new workflows based on your specific solutions

## How It Works

### Overview
1. **Problem Framing** - Define the repetitive task or workflow inefficiency
2. **Assumption Challenging** - Test beliefs about constraints and requirements
3. **Solution Generation** - Brainstorm multiple approaches with different autonomy levels
4. **Solution Selection** - Choose the best balance of autonomy, feasibility, and impact
5. **Experiment Design** - Create a small test to validate the concept
6. **Workflow Generation** - Build a complete YAML workflow + prompt files for your solution

### Key Concepts
- **Autonomy vs. Automation:** We're building semi-autonomous workflows where AI has agency and collaborates with humans, not rigid if-else automation
- **Human-in-the-Loop:** Solutions balance AI initiative with human oversight at key decision points
- **Educational Approach:** Each step explains *why* questions matter, not just what to do
- **Small Experiments:** Test quickly, learn fast, iterate based on real feedback

---

## How to Use This Workflow

### Option 1: In Claude Code (or similar LLM CLI)

If your CLI supports workflow execution:

```bash
Execute workflow 0_ideation_workflow
```

The system will automatically load each step's prompt and guide you through the process.

### Option 2: In ChatGPT, Claude Web, or Any Chat Interface

Copy and paste each step's prompt file in sequence:

#### **Step 1: Problem Framing**
Copy the contents of `step1_problem_framing_prompt.txt` and paste into your chat interface.

The AI will:
- Ask about your repetitive task or workflow
- Help map your current process
- Identify friction points and constraints
- Create a `problem_definition.md` file in `your_workspace/reports/`

**What you'll provide:** Details about your workflow, who it serves, current steps, and desired outcomes

**What you'll get:** A structured problem definition document at `your_workspace/reports/problem_definition.md`

---

#### **Step 2: Assumption Challenging**
Copy the contents of `step2_assumption_challenging_prompt.txt` and paste into your chat.

The AI will:
- List assumptions about your workflow
- Challenge each with focused questions
- Help categorize them as constraints, flexible assumptions, or beliefs to test
- Update `problem_definition.md` with findings

**What you'll provide:** Honest assessment of which assumptions are true constraints vs. inherited beliefs

**What you'll get:** Clear understanding of what's negotiable in your solution design

---

#### **Step 3: Solution Generation**
Copy the contents of `step3_solution_generation_prompt.txt` and paste into your chat.

The AI will:
- Guide you to create 3+ distinct solution approaches
- Use the autonomy spectrum (Assistant → Collaborator → Agent)
- Define AI capabilities and human touchpoints for each
- Document all hypotheses in `problem_definition.md`

**What you'll provide:** Ideas for different ways AI could add autonomy to your workflow

**What you'll get:** Multiple solution options with varying autonomy levels

---

#### **Step 4: Solution Selection**
Copy the contents of `step4_solution_selection_prompt.txt` and paste into your chat.

The AI will:
- Evaluate trade-offs for each solution (autonomy vs. control, complexity vs. impact, etc.)
- Help you choose the most promising approach
- Flesh out the chosen solution with detailed design
- Update `problem_definition.md` with the selected solution

**What you'll provide:** Decisions on which trade-offs you're willing to accept

**What you'll get:** A detailed solution design ready to test

---

#### **Step 5: Experiment Design**
Copy the contents of `step5_experiment_design_prompt.txt` and paste into your chat.

The AI will:
- Help you design a minimal test of your solution
- Define success metrics and criteria
- Create a realistic experiment you can complete in 1-2 weeks
- Document the plan in `problem_definition.md`

**What you'll provide:** Commitment to a small, focused experiment

**What you'll get:** A clear experiment plan with success criteria

---

#### **Step 6: Workflow Generation** ⭐
Copy the contents of `step6_workflow_generation_prompt.txt` and paste into your chat.

The AI will:
- Break your solution into discrete workflow steps
- Generate a YAML workflow file
- Create prompt files for each step
- Build a complete, reusable workflow package in `your_workspace/your_workflows/`
- Create a README for your new workflow

**What you'll provide:** Input on how to structure the workflow steps

**What you'll get:** A complete autonomous workflow at `your_workspace/your_workflows/[workflow_name]/` ready to use in any LLM interface

---

## Expected Outputs

By the end of this workflow, you'll have created:

1. **your_workspace/reports/problem_definition.md** - Complete problem analysis including:
   - Problem statement and current workflow
   - Assumptions analysis
   - Solution hypotheses
   - Chosen solution design
   - Experiment plan

2. **your_workspace/your_workflows/[workflow_name]/** - A complete workflow folder with:
   - YAML workflow structure (`[workflow_name]_workflow.md`)
   - Prompt files for each step
   - README with usage instructions

## Success Metrics

You'll know this workflow succeeded if:
- You have a clear understanding of where autonomy could help your workflow
- You've identified a testable solution approach
- You have an executable experiment plan (1-2 weeks max)
- **You've created a custom workflow you can use repeatedly**
- You feel confident you could create similar workflows for other problems

## Tips for Best Results

### General Tips
- **Be specific:** Vague problems lead to vague solutions. Drill down to concrete tasks.
- **Start small:** Don't try to automate your entire business in one workflow. Focus on one repeatable task.
- **Think autonomy, not automation:** Look for places where AI can take initiative and collaborate, not just follow rigid scripts.

### Problem Selection Tips
- **Good problems:** Weekly reports, research tasks, content drafting, data synthesis, decision frameworks
- **Avoid for now:** One-time projects, highly creative work with no structure, tasks requiring deep domain expertise the AI doesn't have

### During the Workflow
- **Answer questions honestly:** The AI's questions are designed to surface issues early
- **Don't skip assumption challenging:** It often reveals your solution can be simpler than you think
- **Generate truly different solutions:** Avoid three variations of the same idea
- **Keep experiments simple:** If your experiment takes more than 2 weeks, simplify it

### Using Your Generated Workflow
- **Test it yourself first:** Run through your new workflow before sharing it
- **Iterate based on results:** After your experiment, refine the workflow based on what you learned
- **Share with others:** If it works well, your custom workflow can help others with similar problems

## Meta-Learning Opportunity

This workflow is itself a working example of what you're learning to build. Notice:
- How it's structured into discrete steps
- How each prompt guides the AI's behavior
- How it maintains educational context throughout
- How it produces documented outputs at each stage

You can use this same structure for any autonomous workflow you want to create.

## What's Next

After completing this workflow:

1. **Run your experiment** (from Step 5)
2. **Use your custom workflow** (from Step 6)
3. **Iterate based on results**
4. **Identify your next automation opportunity**
5. **Run this workflow again** for a new problem

## Questions or Issues?

This workflow is part of the AI Agents Bootcamp. If you encounter issues or have questions:
- Review the specific step's prompt file for detailed guidance
- Check if you skipped any key questions or outputs
- Consider whether you're trying to solve too large a problem at once

## Philosophy

**Autonomy over Automation:** We're not building rigid robots. We're creating collaborative AI agents that have judgment, ask questions, and work *with* you.

**Education over Execution:** Each step explains the "why" behind the questions, not just the "what." You're learning a thinking framework, not just completing tasks.

**Action over Analysis:** Small experiments beat perfect plans. Build something small, test it, learn, iterate.

**Meta-Capability:** The best outcome isn't just solving one problem—it's learning to systematically identify and design autonomous solutions for any workflow problem you face.

---

**Ready to start?** Begin with Step 1: Problem Framing. Good luck!
