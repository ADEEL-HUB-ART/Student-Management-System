document.addEventListener("DOMContentLoaded", () => {
  const qs = (sel) => document.querySelector(sel);

  const state = {
    get token() {
      return window.localStorage.getItem("token");
    },
    set token(value) {
      if (value) {
        window.localStorage.setItem("token", value);
      } else {
        window.localStorage.removeItem("token");
      }
    },
    get role() {
      return window.localStorage.getItem("role") || "student";
    },
    set role(value) {
      if (value) {
        window.localStorage.setItem("role", value);
      } else {
        window.localStorage.removeItem("role");
      }
    },
  };

  const currentPath = window.location.pathname;

  const requireAuthForPage = () => {
    const publicPaths = ["/login", "/signup"];
    if (!publicPaths.includes(currentPath) && !state.token) {
      window.location.href = "/login";
    }
    if (publicPaths.includes(currentPath) && state.token) {
      window.location.href = "/";
    }
  };

  const setResult = (selector, message, ok = true) => {
    const el = qs(selector);
    if (!el) return;
    if (!message) {
      el.textContent = "";
      el.className = "result";
      return;
    }
    el.className = `result alert ${ok ? "alert-success" : "alert-error"}`;
    el.textContent = message;
  };

  const renderTable = (tableId, rows) => {
    const table = qs(tableId);
    if (!table) return;
    if (!rows || rows.length === 0) {
      table.innerHTML = "";
      return;
    }
    const cols = Object.keys(rows[0]);
    const thead = `<thead><tr>${cols.map((c) => `<th>${c}</th>`).join("")}</tr></thead>`;
    const tbody = `<tbody>${rows
      .map(
        (r) =>
          `<tr>${cols
            .map((c) => `<td>${r[c] != null ? String(r[c]) : ""}</td>`)
            .join("")}</tr>`
      )
      .join("")}</tbody>`;
    table.innerHTML = thead + tbody;
  };

  const apiFetch = async (path, options = {}) => {
    const headers = options.headers ? { ...options.headers } : {};
    headers["Content-Type"] = "application/json";
    if (state.token) {
      headers["token"] = state.token;
    }
    const res = await fetch(path, {
      ...options,
      headers,
    });
    let data = null;
    try {
      data = await res.json();
    } catch {
      // ignore
    }
    if (!res.ok) {
      const detail = data && (data.detail || data.message);
      throw new Error(detail || `Request failed with status ${res.status}`);
    }
    return data;
  };

  const updateRoleTag = () => {
    const tag = qs("#user-role-tag");
    if (tag) {
      const roleLabels = {
        admin: "Admin View",
        teacher: "Teacher View",
        student: "Student View",
      };
      tag.textContent = roleLabels[state.role] || state.role;
    }
  };

  const initLogout = () => {
    const btn = qs("#btn-logout");
    if (!btn) return;
    btn.addEventListener("click", () => {
      state.token = null;
      state.role = null;
      window.location.href = "/login";
    });
  };

  const initSignupPage = () => {
    const form = qs("#signup-form");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      setResult("#signup-result", "");
      const fd = new FormData(form);
      const payload = {
        email: fd.get("email"),
        password: fd.get("password"),
        role: fd.get("role"),
      };
      try {
        await apiFetch("/signup", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setResult("#signup-result", "Signup successful. Redirecting to login…", true);
        setTimeout(() => {
          window.location.href = "/login";
        }, 900);
      } catch (err) {
        setResult("#signup-result", err.message, false);
      }
    });
  };

  const initLoginPage = () => {
    const form = qs("#login-form");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      setResult("#login-result", "");
      const fd = new FormData(form);
      const payload = {
        email: fd.get("email"),
        password: fd.get("password"),
      };
      try {
        const data = await apiFetch("/login", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        state.token = data.access_token;
        state.role = data.role;
        setResult("#login-result", "Login successful. Redirecting to home…", true);
        setTimeout(() => {
          window.location.href = "/";
        }, 700);
      } catch (err) {
        setResult("#login-result", err.message, false);
      }
    });
  };

  const initHomeDashboard = () => {
    const btn = qs("#btn-home-load-dashboard");
    const grid = qs("#home-dashboard-grid");
    const announcementsEl = qs("#home-announcements");
    if (!btn || !grid) return;

    updateRoleTag();

    const loadDashboard = async () => {
      grid.innerHTML = '<div class="alert">Loading...</div>';
      try {
        const data = await apiFetch("/dashboard/");
        const cards = [
          { label: "Total Students", value: data.total_students },
          { label: "Departments", value: data.total_departments },
          { label: "Subjects", value: data.total_subjects },
          { label: "Fees Paid", value: data.fees?.paid },
          { label: "Fees Unpaid", value: data.fees?.unpaid },
          { label: "Cleared", value: data.clearance?.cleared_students },
          { label: "Not Cleared", value: data.clearance?.not_cleared_students },
          { label: "Avg GPA", value: data.average_gpa },
        ];
        grid.innerHTML = cards
          .map(
            (c) => `
          <div class="dashboard-card">
            <div class="dashboard-card-label">${c.label}</div>
            <div class="dashboard-card-value">${c.value ?? "—"}</div>
          </div>`
          )
          .join("");
      } catch (err) {
        grid.innerHTML = `<div class="alert alert-error">${err.message}</div>`;
      }
    };

    const loadAnnouncements = async () => {
      if (!announcementsEl) return;
      try {
        const data = await apiFetch("/announcements/");
        if (data.length === 0) {
          announcementsEl.innerHTML = '<p class="card-help">No announcements yet.</p>';
          return;
        }
        announcementsEl.innerHTML = data.slice(0, 3).map(a => `
          <div class="announcement-card">
            <div class="announcement-header">
              <span class="announcement-title">${a.title}</span>
              <span class="priority-badge priority-${a.priority}">${a.priority}</span>
            </div>
            <p class="announcement-content">${a.content.substring(0, 100)}${a.content.length > 100 ? '...' : ''}</p>
          </div>
        `).join("");
      } catch (err) {
        announcementsEl.innerHTML = '<p class="card-help">Could not load announcements.</p>';
      }
    };

    btn.addEventListener("click", loadDashboard);
    loadDashboard();
    loadAnnouncements();
  };

  // ================== STUDENTS PAGE ==================
  const initStudentsPage = () => {
    const form = qs("#students-create-form");
    const refreshBtn = qs("#students-refresh-btn");
    const searchInput = qs("#students-search-input");
    const tableId = "#students-table";
    let allStudents = [];

    const formCard = form?.closest(".card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadStudents = async () => {
      try {
        const data = await apiFetch("/students/");
        allStudents = data;
        renderTable(tableId, data);
        setResult("#students-list-result", `Loaded ${data.length} students.`, true);
      } catch (err) {
        allStudents = [];
        renderTable(tableId, []);
        setResult("#students-list-result", err.message, false);
      }
    };

    const applySearch = () => {
      if (!searchInput || !allStudents.length) return;
      const term = searchInput.value.trim().toLowerCase();
      if (!term) {
        renderTable(tableId, allStudents);
        return;
      }
      const filtered = allStudents.filter((s) =>
        [s.name, s.email, s.roll_no]
          .filter(Boolean)
          .some((v) => String(v).toLowerCase().includes(term))
      );
      renderTable(tableId, filtered);
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#students-create-result", "");
        const fd = new FormData(form);
        const payload = {
          name: fd.get("name"),
          age: Number(fd.get("age")),
          semester: Number(fd.get("semester")),
          department_id: Number(fd.get("department_id")),
          email: fd.get("email"),
          roll_no: fd.get("roll_no"),
        };
        try {
          const data = await apiFetch("/students/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#students-create-result", `Student created with ID ${data.id}.`, true);
          form.reset();
          loadStudents();
        } catch (err) {
          setResult("#students-create-result", err.message, false);
        }
      });
    }

    if (refreshBtn) {
      refreshBtn.addEventListener("click", loadStudents);
      loadStudents();
    }

    if (searchInput) {
      searchInput.addEventListener("input", applySearch);
    }
  };

  // ================== DEPARTMENTS PAGE ==================
  const initDepartmentsPage = () => {
    const form = qs("#departments-create-form");
    const refreshBtn = qs("#departments-refresh-btn");
    const tableId = "#departments-table";

    const formCard = qs("#department-add-card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadDepartments = async () => {
      try {
        const data = await apiFetch("/departments/");
        renderTable(tableId, data);
        setResult("#departments-list-result", `Loaded ${data.length} departments.`, true);
      } catch (err) {
        renderTable(tableId, []);
        setResult("#departments-list-result", err.message, false);
      }
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#departments-create-result", "");
        const fd = new FormData(form);
        const payload = {
          name: fd.get("name"),
          hod: fd.get("hod"),
        };
        try {
          const data = await apiFetch("/departments/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#departments-create-result", `Department created with ID ${data.id}.`, true);
          form.reset();
          loadDepartments();
        } catch (err) {
          setResult("#departments-create-result", err.message, false);
        }
      });
    }

    if (refreshBtn) {
      refreshBtn.addEventListener("click", loadDepartments);
      loadDepartments();
    }
  };

  // ================== SUBJECTS PAGE ==================
  const initSubjectsPage = () => {
    const form = qs("#subjects-create-form");
    const refreshBtn = qs("#subjects-refresh-btn");
    const tableId = "#subjects-table";

    const formCard = qs("#subject-add-card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadSubjects = async () => {
      try {
        const data = await apiFetch("/subjects/");
        renderTable(tableId, data);
        setResult("#subjects-list-result", `Loaded ${data.length} subjects.`, true);
      } catch (err) {
        renderTable(tableId, []);
        setResult("#subjects-list-result", err.message, false);
      }
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#subjects-create-result", "");
        const fd = new FormData(form);
        const payload = {
          name: fd.get("name"),
          semester: Number(fd.get("semester")),
          teacher: fd.get("teacher"),
          department_id: Number(fd.get("department_id")),
        };
        try {
          const data = await apiFetch("/subjects/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#subjects-create-result", `Subject created with ID ${data.id}.`, true);
          form.reset();
          loadSubjects();
        } catch (err) {
          setResult("#subjects-create-result", err.message, false);
        }
      });
    }

    if (refreshBtn) {
      refreshBtn.addEventListener("click", loadSubjects);
      loadSubjects();
    }
  };

  // ================== RESULTS PAGE ==================
  const initResultsPage = () => {
    const form = qs("#results-create-form");
    const searchBtn = qs("#results-search-btn");
    const searchInput = qs("#results-student-id-input");
    const tableId = "#results-table";

    const formCard = qs("#result-add-card");
    if (formCard && !["teacher", "admin"].includes(state.role)) {
      formCard.style.display = "none";
    }

    const loadResults = async (studentId) => {
      try {
        const data = await apiFetch(`/results/student/${studentId}`);
        renderTable(tableId, data);
        setResult("#results-list-result", `Loaded ${data.length} results.`, true);
      } catch (err) {
        renderTable(tableId, []);
        setResult("#results-list-result", err.message, false);
      }
    };

    if (form && ["teacher", "admin"].includes(state.role)) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#results-create-result", "");
        const fd = new FormData(form);
        const payload = {
          student_id: Number(fd.get("student_id")),
          subject_id: Number(fd.get("subject_id")),
          midterm_marks: Number(fd.get("midterm_marks")),
          sessional_marks: Number(fd.get("sessional_marks")),
          final_marks: Number(fd.get("final_marks")),
          total_marks: Number(fd.get("total_marks")),
        };
        try {
          const data = await apiFetch("/results/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#results-create-result", `Result created with ID ${data.id}.`, true);
          form.reset();
        } catch (err) {
          setResult("#results-create-result", err.message, false);
        }
      });
    }

    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", () => {
        const studentId = searchInput.value.trim();
        if (studentId) {
          loadResults(studentId);
        } else {
          setResult("#results-list-result", "Please enter a Student ID.", false);
        }
      });
    }
  };

  // ================== FEES PAGE ==================
  const initFeesPage = () => {
    const form = qs("#fees-create-form");
    const updateForm = qs("#fees-update-form");
    const searchBtn = qs("#fees-search-btn");
    const searchInput = qs("#fees-student-id-input");
    const tableId = "#fees-table";
    const summaryEl = qs("#fees-summary");
    const updateSection = qs("#fee-update-section");

    const formCard = qs("#fee-add-card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadFees = async (studentId) => {
      try {
        const data = await apiFetch(`/fees/student/${studentId}`);
        renderTable(tableId, data);
        setResult("#fees-list-result", `Loaded ${data.length} fee records.`, true);

        // Show summary
        if (summaryEl && data.length > 0) {
          const totalFees = data.reduce((sum, f) => sum + f.total_fee, 0);
          const totalPaid = data.reduce((sum, f) => sum + f.paid_amount, 0);
          const totalDue = data.reduce((sum, f) => sum + f.due_amount, 0);
          summaryEl.innerHTML = `
            <div class="fee-stat">
              <div class="fee-stat-label">Total Fees</div>
              <div class="fee-stat-value">₨${totalFees.toLocaleString()}</div>
            </div>
            <div class="fee-stat">
              <div class="fee-stat-label">Paid</div>
              <div class="fee-stat-value paid">₨${totalPaid.toLocaleString()}</div>
            </div>
            <div class="fee-stat">
              <div class="fee-stat-label">Due</div>
              <div class="fee-stat-value due">₨${totalDue.toLocaleString()}</div>
            </div>
          `;
        }

        if (updateSection && state.role === "admin") {
          updateSection.style.display = "block";
        }
      } catch (err) {
        renderTable(tableId, []);
        setResult("#fees-list-result", err.message, false);
        if (summaryEl) summaryEl.innerHTML = "";
      }
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#fees-create-result", "");
        const fd = new FormData(form);
        const payload = {
          student_id: Number(fd.get("student_id")),
          semester: Number(fd.get("semester")),
          total_fee: Number(fd.get("total_fee")),
          paid_amount: Number(fd.get("paid_amount")) || 0,
        };
        try {
          const data = await apiFetch("/fees/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#fees-create-result", `Fee record created with ID ${data.id}.`, true);
          form.reset();
        } catch (err) {
          setResult("#fees-create-result", err.message, false);
        }
      });
    }

    if (updateForm && state.role === "admin") {
      updateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#fees-update-result", "");
        const fd = new FormData(updateForm);
        const feeId = fd.get("fee_id");
        const paidAmount = Number(fd.get("paid_amount"));
        try {
          await apiFetch(`/fees/${feeId}?paid_amount=${paidAmount}`, {
            method: "PUT",
          });
          setResult("#fees-update-result", "Payment recorded successfully.", true);
          updateForm.reset();
        } catch (err) {
          setResult("#fees-update-result", err.message, false);
        }
      });
    }

    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", () => {
        const studentId = searchInput.value.trim();
        if (studentId) {
          loadFees(studentId);
        } else {
          setResult("#fees-list-result", "Please enter a Student ID.", false);
        }
      });
    }
  };

  // ================== CLEARANCE PAGE ==================
  const initClearancePage = () => {
    const form = qs("#clearance-create-form");
    const searchBtn = qs("#clearance-search-btn");
    const searchInput = qs("#clearance-student-id-input");
    const statusCard = qs("#clearance-status-card");

    const formCard = qs("#clearance-add-card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadClearance = async (studentId) => {
      try {
        const data = await apiFetch(`/clearance/student/${studentId}`);
        setResult("#clearance-list-result", "Clearance loaded.", true);

        if (statusCard) {
          statusCard.style.display = "block";
          qs("#clearance-student-display").textContent = studentId;

          const badge = qs("#clearance-overall-badge");
          badge.textContent = data.is_cleared ? "FULLY CLEARED" : "NOT CLEARED";
          badge.className = `clearance-badge ${data.is_cleared ? "cleared" : "not-cleared"}`;

          const updateItem = (id, cleared) => {
            const statusEl = qs(`#clearance-${id} .clearance-status`);
            if (statusEl) {
              statusEl.textContent = cleared ? "YES" : "NO";
              statusEl.className = `clearance-status ${cleared ? "yes" : "no"}`;
            }
          };

          updateItem("library", data.library_clearance);
          updateItem("finance", data.finance_clearance);
          updateItem("hostel", data.hostel_clearance);
          updateItem("department", data.department_clearance);
        }
      } catch (err) {
        if (statusCard) statusCard.style.display = "none";
        setResult("#clearance-list-result", err.message, false);
      }
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#clearance-create-result", "");
        const fd = new FormData(form);
        const payload = {
          student_id: Number(fd.get("student_id")),
          library_clearance: fd.get("library_clearance") === "on",
          finance_clearance: fd.get("finance_clearance") === "on",
          hostel_clearance: fd.get("hostel_clearance") === "on",
          department_clearance: fd.get("department_clearance") === "on",
        };
        try {
          const data = await apiFetch("/clearance/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#clearance-create-result", `Clearance created/updated for student.`, true);
          form.reset();
        } catch (err) {
          setResult("#clearance-create-result", err.message, false);
        }
      });
    }

    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", () => {
        const studentId = searchInput.value.trim();
        if (studentId) {
          loadClearance(studentId);
        } else {
          setResult("#clearance-list-result", "Please enter a Student ID.", false);
        }
      });
    }
  };

  // ================== GPA PAGE ==================
  const initGpaPage = () => {
    const form = qs("#gpa-form");
    const cgpaBtn = qs("#cgpa-btn");
    const displayCard = qs("#gpa-display-card");

    const displayGpa = (gpaVal, cgpaVal, studentId, semester) => {
      if (!displayCard) return;
      displayCard.style.display = "block";

      qs("#gpa-student-info").textContent = `Student #${studentId}${semester ? ` | Semester ${semester}` : ""}`;

      if (gpaVal !== null) {
        qs("#gpa-value").textContent = gpaVal.toFixed(2);
        qs("#gpa-bar").style.width = `${(gpaVal / 4) * 100}%`;
      }

      if (cgpaVal !== null) {
        qs("#cgpa-value").textContent = cgpaVal.toFixed(2);
        qs("#cgpa-bar").style.width = `${(cgpaVal / 4) * 100}%`;
      }
    };

    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#gpa-result", "");
        const fd = new FormData(form);
        const studentId = fd.get("student_id");
        const semester = fd.get("semester");

        try {
          const data = await apiFetch(`/students/${studentId}/gpa/${semester}`);
          setResult("#gpa-result", `GPA for semester ${semester}: ${data.GPA}`, true);
          displayGpa(data.GPA, null, studentId, semester);

          // Also fetch CGPA
          try {
            const cgpaData = await apiFetch(`/students/${studentId}/cgpa`);
            qs("#cgpa-value").textContent = cgpaData.CGPA.toFixed(2);
            qs("#cgpa-bar").style.width = `${(cgpaData.CGPA / 4) * 100}%`;
          } catch { }
        } catch (err) {
          setResult("#gpa-result", err.message, false);
        }
      });
    }

    if (cgpaBtn) {
      cgpaBtn.addEventListener("click", async () => {
        setResult("#gpa-result", "");
        const studentId = qs("#gpa-student-id")?.value;
        if (!studentId) {
          setResult("#gpa-result", "Please enter a Student ID.", false);
          return;
        }
        try {
          const data = await apiFetch(`/students/${studentId}/cgpa`);
          setResult("#gpa-result", `CGPA: ${data.CGPA}`, true);
          displayGpa(null, data.CGPA, studentId, null);
          qs("#gpa-value").textContent = "--";
          qs("#gpa-bar").style.width = "0%";
        } catch (err) {
          setResult("#gpa-result", err.message, false);
        }
      });
    }
  };

  // ================== ANNOUNCEMENTS PAGE ==================
  const initAnnouncementsPage = () => {
    const form = qs("#announcements-create-form");
    const refreshBtn = qs("#announcements-refresh-btn");
    const listEl = qs("#announcements-list");

    const formCard = qs("#announcement-add-card");
    if (formCard && state.role !== "admin") {
      formCard.style.display = "none";
    }

    const loadAnnouncements = async () => {
      if (!listEl) return;
      try {
        const data = await apiFetch("/announcements/");
        if (data.length === 0) {
          listEl.innerHTML = '<p class="card-help">No announcements yet.</p>';
          setResult("#announcements-list-result", "No announcements.", true);
          return;
        }
        listEl.innerHTML = data.map(a => `
          <div class="announcement-card">
            <div class="announcement-header">
              <span class="announcement-title">${a.title}</span>
              <span class="priority-badge priority-${a.priority}">${a.priority}</span>
            </div>
            <p class="announcement-content">${a.content}</p>
            <div class="announcement-meta">Posted by ${a.posted_by} on ${new Date(a.created_at).toLocaleDateString()}</div>
          </div>
        `).join("");
        setResult("#announcements-list-result", `Loaded ${data.length} announcements.`, true);
      } catch (err) {
        listEl.innerHTML = "";
        setResult("#announcements-list-result", err.message, false);
      }
    };

    if (form && state.role === "admin") {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#announcements-create-result", "");
        const fd = new FormData(form);
        const payload = {
          title: fd.get("title"),
          content: fd.get("content"),
          priority: fd.get("priority"),
        };
        try {
          await apiFetch("/announcements/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          setResult("#announcements-create-result", "Announcement posted!", true);
          form.reset();
          loadAnnouncements();
        } catch (err) {
          setResult("#announcements-create-result", err.message, false);
        }
      });
    }

    if (refreshBtn) {
      refreshBtn.addEventListener("click", loadAnnouncements);
    }

    loadAnnouncements();
  };

  // ================== TEACHERS PAGE ==================
  const initTeachersPage = () => {
    const refreshBtn = qs("#teachers-refresh-btn");
    const gridEl = qs("#teachers-grid");

    const loadTeachers = async () => {
      if (!gridEl) return;
      try {
        const data = await apiFetch("/teachers/");
        if (data.length === 0) {
          gridEl.innerHTML = '<p class="card-help">No teachers found.</p>';
          setResult("#teachers-list-result", "No teachers in system.", true);
          return;
        }
        gridEl.innerHTML = data.map(t => `
          <div class="teacher-card">
            <div class="teacher-avatar">👨‍🏫</div>
            <div class="teacher-name">${t.name}</div>
            <div class="teacher-subjects">${t.subject_count} subject${t.subject_count > 1 ? 's' : ''}</div>
          </div>
        `).join("");
        setResult("#teachers-list-result", `Found ${data.length} teachers.`, true);
      } catch (err) {
        gridEl.innerHTML = "";
        setResult("#teachers-list-result", err.message, false);
      }
    };

    if (refreshBtn) {
      refreshBtn.addEventListener("click", loadTeachers);
    }

    loadTeachers();
  };

  // ================== PROFILE PAGE ==================
  const initProfilePage = () => {
    const passwordForm = qs("#password-change-form");
    const clearCacheBtn = qs("#btn-clear-cache");
    const logoutAllBtn = qs("#btn-logout-all");

    const loadProfile = async () => {
      try {
        const data = await apiFetch("/profile/me");
        qs("#profile-email").textContent = data.email;
        qs("#profile-role").textContent = data.role.toUpperCase();
        qs("#profile-id").textContent = `#${data.id}`;
      } catch (err) {
        setResult("#profile-load-result", err.message, false);
      }
    };

    if (passwordForm) {
      passwordForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        setResult("#password-change-result", "");
        const fd = new FormData(passwordForm);
        const newPw = fd.get("new_password");
        const confirmPw = fd.get("confirm_password");

        if (newPw !== confirmPw) {
          setResult("#password-change-result", "New passwords don't match.", false);
          return;
        }

        const payload = {
          current_password: fd.get("current_password"),
          new_password: newPw,
        };
        try {
          await apiFetch("/profile/password", {
            method: "PUT",
            body: JSON.stringify(payload),
          });
          setResult("#password-change-result", "Password changed successfully!", true);
          passwordForm.reset();
        } catch (err) {
          setResult("#password-change-result", err.message, false);
        }
      });
    }

    if (clearCacheBtn) {
      clearCacheBtn.addEventListener("click", () => {
        localStorage.clear();
        alert("Local storage cleared. You will be redirected to login.");
        window.location.href = "/login";
      });
    }

    if (logoutAllBtn) {
      logoutAllBtn.addEventListener("click", () => {
        state.token = null;
        state.role = null;
        window.location.href = "/login";
      });
    }

    loadProfile();
  };

  // ================== BOOTSTRAP ==================
  requireAuthForPage();
  initLogout();
  initSignupPage();
  initLoginPage();
  initHomeDashboard();
  initStudentsPage();
  initDepartmentsPage();
  initSubjectsPage();
  initResultsPage();
  initFeesPage();
  initClearancePage();
  initGpaPage();
  initAnnouncementsPage();
  initTeachersPage();
  initProfilePage();
});
