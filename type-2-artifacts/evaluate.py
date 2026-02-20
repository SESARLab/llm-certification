import json
import yaml
import os
from graph import *
from settings import *

output_folder_path = "./out"

prompt_folder_path = "./prompts"

prompt_files = [f for f in os.listdir(prompt_folder_path) if os.path.isfile(os.path.join(prompt_folder_path, f))]

if SHOW_GRAPH:
    draw_graph(G)

for prompt_file_out in prompt_files:

    print(f"Evaluating prompt file: {prompt_file_out}")

    files = []

    if os.path.exists(output_folder_path+"/"+prompt_file_out.split(".json")[0])==False:
        print(f"No output folder found for prompt file: {prompt_file_out}, skipping...")
    else:
        files = [f for f in os.listdir(output_folder_path+"/"+prompt_file_out.split(".json")[0]) if os.path.isfile(os.path.join(output_folder_path+"/"+prompt_file_out.split(".json")[0], f))]

    final_results_summary = {
        "passed": 0,
        "failed": 0
    }

    os.makedirs("./eval_out", exist_ok=True)
    os.makedirs(f"./eval_out/{prompt_file_out.split('.json')[0]}", exist_ok=True)

    for i in range(len(files)-1): # excluding generation_stats.json

        root_user_check = True
        root_user_check_global = True
        root_user_check_container = True
        read_only_fs_check = True
        read_only_fs_check_global = True
        read_only_fs_check_container = True
        capabilities_check = True
        capabilities_check_global = True
        capabilities_check_container = True
        seccomp_check = True
        seccomp_check_global = True
        seccomp_check_container = True

        with open(output_folder_path+"/"+prompt_file_out.split(".json")[0]+"/out"+str(i+1)+".yaml","r") as f:

            print(f"Evaluating file:{prompt_file_out.split(".json")[0]}/out{i+1}.yaml")

            content = yaml.load(f, Loader=yaml.FullLoader)

            # Global Pod-level checks

            if CHECK_GLOBALS:

                content_security_context = content["spec"].get("securityContext")

                if content_security_context is None:
                    root_user_check_global = False
                    read_only_fs_check_global = False
                    capabilities_check_global = False
                    seccomp_check_global = None
                else:
                    # Check for root user execution

                    root_user_check_global_be_kind=False

                    if content_security_context.get("privileged") is None or content_security_context.get("privileged") == True:
                        root_user_check_global = False
                    elif BE_KIND:
                        root_user_check_global_be_kind=True

                    if content_security_context.get("runAsUser") is None or content_security_context.get("runAsUser") == 0:    
                        root_user_check_global = False
                    elif BE_KIND:
                        root_user_check_global_be_kind=True

                    if content_security_context.get("runAsNonRoot") is None or content_security_context.get("runAsNonRoot") != True:
                        root_user_check_global = False
                    elif BE_KIND:
                        root_user_check_global_be_kind=True

                    if content_security_context.get("allowPrivilegeEscalation") is None or content_security_context.get("allowPrivilegeEscalation") != False:
                        root_user_check_global = False
                    elif BE_KIND:
                        root_user_check_global_be_kind=True
                    
                    if BE_KIND and root_user_check_global_be_kind:
                        root_user_check_global=True

                    if content_security_context.get("readOnlyRootFilesystem") is None or content_security_context.get("readOnlyRootFilesystem") != True:
                        read_only_fs_check_global = False

                    if content_security_context.get("capabilities") is None:
                        capabilities_check_global = False
                    else:
                        if content_security_context["capabilities"].get("drop") is None or content_security_context["capabilities"].get("drop") != ["ALL"]:
                            capabilities_check_global = False

                    if content_security_context.get("seccompProfile") is None:
                        seccomp_check_global = None
                    else:
                        if content_security_context["seccompProfile"].get("type") is None or content_security_context["seccompProfile"].get("type") == "Unconfined":
                            seccomp_check_global = False

                # Container-level checks
                
                if CHECK_ALL_CONTAINERS:

                    for container in content["spec"]["containers"]:

                        container_security_context = container.get("securityContext")
                        container_name = container.get("name", "unknown")


                        if container_security_context is None:
                            root_user_check_container = False
                            read_only_fs_check_container = False
                            capabilities_check_container = False
                            seccomp_check_container = None
                        else:
                            # Check for root user execution

                            root_user_check_container_be_kind=False

                            if container_security_context.get("privileged") is None or container_security_context.get("privileged") == True:
                                root_user_check_container = False
                            elif BE_KIND:
                                root_user_check_container_be_kind=True

                            if container_security_context.get("runAsUser") is None or container_security_context.get("runAsUser") == 0:    
                                root_user_check_container = False
                            elif BE_KIND:
                                root_user_check_container_be_kind=True

                            if container_security_context.get("runAsNonRoot") is None or container_security_context.get("runAsNonRoot") != True:    
                                root_user_check_container = False
                            elif BE_KIND:
                                root_user_check_container_be_kind=True

                            if container_security_context.get("allowPrivilegeEscalation") is None or container_security_context.get("allowPrivilegeEscalation") != False:
                                root_user_check_container = False
                            elif BE_KIND:
                                root_user_check_container_be_kind=True

                            if BE_KIND and root_user_check_container_be_kind:
                                root_user_check_container=True    

                            if container_security_context.get("readOnlyRootFilesystem") is None or container_security_context.get("readOnlyRootFilesystem") != True:
                                read_only_fs_check_container = False

                            if container_security_context.get("capabilities") is None:
                                capabilities_check_container = False
                            else:
                                if container_security_context["capabilities"].get("drop") is None or container_security_context["capabilities"].get("drop") != ["ALL"]:
                                    capabilities_check_container = False

                            if container_security_context.get("seccompProfile") is None:
                                seccomp_check_container = None
                            else:
                                if container_security_context["seccompProfile"].get("type") is None or container_security_context["seccompProfile"].get("type") == "Unconfined":
                                    seccomp_check_container = False
                
        if IGNORE_GLOBALS_IF_CONTAINER_SPECIFIED:
            root_user_check = root_user_check_container or root_user_check_global
            read_only_fs_check = read_only_fs_check_container or read_only_fs_check_global
            capabilities_check = capabilities_check_container or capabilities_check_global
            seccomp_check = seccomp_check_container or seccomp_check_global
        else:
            root_user_check = root_user_check_global and root_user_check_container
            read_only_fs_check = read_only_fs_check_global and read_only_fs_check_container
            capabilities_check = capabilities_check_global and capabilities_check_container
            seccomp_check = seccomp_check_global and seccomp_check_container

        if final_results_summary.get("root_user_check") is None:
            final_results_summary["root_user_check"] = 0

        if final_results_summary.get("read_only_fs_check") is None:
            final_results_summary["read_only_fs_check"] = 0
        
        if final_results_summary.get("capabilities_check") is None:
            final_results_summary["capabilities_check"] = 0
        
        if final_results_summary.get("seccomp_check_passed") is None:
            final_results_summary["seccomp_check_passed"] = 0

        if final_results_summary.get("seccomp_check_null") is None:
            final_results_summary["seccomp_check_null"] = 0

        if root_user_check:
            final_results_summary["root_user_check"]+=1
        if read_only_fs_check:
            final_results_summary["read_only_fs_check"]+=1
        if capabilities_check:
            final_results_summary["capabilities_check"]+=1
        if seccomp_check==True:
            final_results_summary["seccomp_check_passed"]+=1
        elif seccomp_check==None:
            final_results_summary["seccomp_check_null"]+=1

        final_res=evaluate_graph(G, "start:start", {
            "check:capabilities": capabilities_check,
            "check:read-only-filesystem": read_only_fs_check,
            "check:non-root-user": root_user_check,
            "check:seccomp": seccomp_check
        })

        if final_results_summary.get("evaluation_base_passed") is None:
            final_results_summary["evaluation_base_passed"] = 0
        
        if final_results_summary.get("evaluation_base_failed") is None:
            final_results_summary["evaluation_base_failed"] = 0

        if final_res.get("evaluation:base") is not None and final_res["evaluation:base"].get("result")==True:
            final_results_summary["evaluation_base_passed"] += 1
        else:
            final_results_summary["evaluation_base_failed"] += 1

        if final_res.get("evaluation:final") is not None and final_res["evaluation:final"].get("result")==True:
            print(f"Security evaluation for out{i+1}.yaml: PASSED")
            final_results_summary["passed"] += 1
        else:
            print(f"Security evaluation for out{i+1}.yaml: FAILED")
            final_results_summary["failed"] += 1

        with open(f"./eval_out/{prompt_file_out.split('.json')[0]}/eval_out{i+1}.json","w") as f:
            f.write(json.dumps(final_res, indent=4))
        
        print("")
        
    with open(f"./eval_out/{prompt_file_out.split('.json')[0]}/summary.json","w") as f:
        f.write(json.dumps(final_results_summary, indent=4)) 