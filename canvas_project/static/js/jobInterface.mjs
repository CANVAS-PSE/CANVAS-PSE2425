export class JobInterface {
    #jobInterfaceBody;
    /**
     * @type {Job[]}
     */
    #jobList = [];

    constructor() {
        this.#jobInterfaceBody = document.getElementById("jobInterfaceBody");

        document
            .getElementById("createNewJob")
            .addEventListener("click", () => {
                this.#createNewJob();
            });

        /**
         * Update when opening
         */
        document
            .getElementById("jobInterfaceToggle")
            .addEventListener("click", () => {
                if (this.#jobList.length == 0) {
                    this.#jobInterfaceBody.innerHTML =
                        "You currently have no jobs.";
                }
                this.#jobList.forEach((job) => job.fetchStatus());
            });

        /**
         * Update job status every 5 seconds when modal is open
         */
        setInterval(() => {
            if (this.#jobInterfaceBody.checkVisibility()) {
                this.#jobList.forEach((job) => job.fetchStatus());
            }
        }, 5000);
    }

    #createNewJob() {
        fetch(window.location.origin + "/jobs/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.#getCookie("csrftoken"),
            },
        })
            .then((res) => res.json())
            .then((data) => {
                const newJob = new Job(this, data.jobID);
                if (this.#jobList.length == 0) {
                    this.#jobInterfaceBody.innerHTML = "";
                }
                this.#jobList.push(newJob);
                this.#jobInterfaceBody.prepend(newJob);
                document
                    .getElementById("hasActiveJobsIndicator")
                    .classList.remove("d-none");
            })
            .catch((error) => {
                console.error("Error creating new job:", error);
            });
    }

    /**
     *
     * @param {Job} job the job you want to delete
     */
    deleteJob(job) {
        this.#jobList.splice(this.#jobList.indexOf(job));
        job.remove();
        if (this.#jobList.length == 0) {
            this.#jobInterfaceBody.innerHTML = "You currently have no jobs.";
            document
                .getElementById("hasActiveJobsIndicator")
                .classList.add("d-none");
        }
    }

    /**
     * Gets the cookie specified by the name
     * @param {String} name The name of the cookie you want to get.
     * @returns the cookie or null if it couldn't be found.
     */
    #getCookie(name) {
        if (!document.cookie) {
            return null;
        }

        // document.cookie is a key=value list separated by ';'
        const xsrfCookies = document.cookie
            .split(";")
            .map((c) => c.trim())
            //filter the right cookie name
            .filter((c) => c.startsWith(name + "="));

        if (xsrfCookies.length === 0) {
            return null;
        }
        // return the decoded value of the first cookie found
        return decodeURIComponent(xsrfCookies[0].split("=")[1]);
    }
}

export class Job extends HTMLElement {
    #id;
    #jobInterface;
    #progress = 0.8;
    #isFinished = false;

    #statusElem;
    #progressElem;
    #resultButton;

    constructor(jobInterface, jobID) {
        super();
        this.#id = jobID;
        this.#jobInterface = jobInterface;

        this.#createJobElement();
    }

    #createJobElement() {
        this.classList.add(
            "rounded-3",
            "bg-body-secondary",
            "d-flex",
            "p-2",
            "gap-2",
            "align-items-center"
        );

        const jobName = document.createElement("div");
        jobName.classList.add("fw-bolder", "text-nowrap");
        jobName.innerHTML = "Job " + this.#id;
        this.appendChild(jobName);

        this.#statusElem = document.createElement("div");
        this.#statusElem.classList.add("text-secondary", "text-nowrap");
        this.appendChild(this.#statusElem);

        const progressBar = document.createElement("div");
        progressBar.classList.add("progress", "w-100", "bg-body");

        this.#progressElem = document.createElement("div");
        this.#progressElem.classList.add("progress-bar");
        this.#progressElem.style.width = this.#progress * 100 + "%";
        this.#progressElem.setAttribute("role", "progressbar");
        this.#progressElem.setAttribute(
            "aria-valuenow",
            (this.#progress * 100).toString()
        );
        this.#progressElem.setAttribute("aria-valuemin", "0");
        this.#progressElem.setAttribute("aria-valuemax", "100");

        progressBar.appendChild(this.#progressElem);
        this.appendChild(progressBar);

        this.#resultButton = document.createElement("a");
        this.#resultButton.classList.add(
            "btn",
            "btn-primary",
            "text-nowrap",
            "rouned-3"
        );
        this.#resultButton.innerHTML = "View Result";
        this.#resultButton.classList.add("d-none");
        this.appendChild(this.#resultButton);

        const deleteButton = document.createElement("button");
        deleteButton.classList.add("btn", "btn-danger", "text-nowrap");
        deleteButton.innerHTML = "<i class='bi bi-trash'></i>";
        deleteButton.addEventListener("click", () => {
            this.#jobInterface.deleteJob(this);
            // Optionally, you can add code to remove the job from the job list and server
        });
        this.appendChild(deleteButton);
    }

    fetchStatus() {
        if (!this.#isFinished) {
            fetch(window.location.origin + "/jobs/" + this.#id)
                .then((res) => res.json())
                .then((data) => {
                    this.#statusElem.innerHTML = "Status: " + data["status"];
                    this.#progressElem.setAttribute(
                        "aria-valuenow",
                        (data["progress"] * 100).toString()
                    );
                    this.#progressElem.style.width =
                        data["progress"] * 100 + "%";
                    if (data["progress"] >= 1) {
                        this.#resultButton.classList.toggle("d-none");
                        this.#resultButton.href =
                            window.location.origin + data["result"];
                        this.#isFinished = true;
                    }
                })
                .catch((error) => {
                    console.error("Error creating new job:", error);
                });
        }
    }
}

customElements.define("job-element", Job);
