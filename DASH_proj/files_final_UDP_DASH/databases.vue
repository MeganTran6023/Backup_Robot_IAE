<template id="databases">
  <div class="app-container">
    <!-- Sidebar -->
    <aside :class="['sidebar', { collapsed: !sidebarOpen }]">
      <div class="sidebar-header">
        <template v-if="sidebarOpen">
          <span>DASH</span>
        </template>
        <template v-else>
          <span class="icon-only">☁️</span>
        </template>
      </div>
      <div class="sidebar-subheader">
        <template v-if="sidebarOpen">
          <p class="font-bold mb-4">Logged in as: {{username}}</p>
        </template>
      </div>
      <ul class="sidebar-menu">
        <li class="menu-item" @click="navigateToHome">
          <span class="icon">📡</span>
          <span v-if="sidebarOpen" class="label">Sensors</span>
        </li>
        <li class="menu-item active">
          <span class="icon">🧮</span>
          <span v-if="sidebarOpen" class="label">Databases</span>
        </li>
        <li class="menu-item">
          <span class="icon">⚙️</span>
          <span v-if="sidebarOpen" class="label">Settings</span>
        </li>
      </ul>
      <div class="sidebar-subheader">
        <template v-if="sidebarOpen">
          <button class="logout-btn" @click="logout()">Logout</button>
        </template>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <button class="toggle-btn" @click="toggleButton()">☰</button>

      <!-- Toast Notification -->
      <transition name="toast-fade">
        <div v-if="toast.show" :class="['toast-notification', toast.type]">
          {{ toast.message }} {{ toast.type === 'success' ? '✓' : '✕' }}
        </div>
      </transition>

      <!-- Delete Confirmation Modal -->
      <div v-if="deleteModalCollection" class="delete-modal-overlay">
        <div class="delete-modal">
          <h3 class="delete-modal-title">Confirm Deletion</h3>
          <p class="delete-modal-message">
            Are you sure you want to permanently delete <strong>{{ deleteModalCollection }}</strong>?
          </p>
          <p class="delete-modal-warning">This cannot be undone.</p>
          <div class="delete-modal-buttons">
            <button class="delete-modal-btn delete-modal-btn-no" @click="deleteModalCollection = null">No</button>
            <button class="delete-modal-btn delete-modal-btn-yes" @click="confirmDelete">Yes</button>
          </div>
        </div>
      </div>

      <!-- Database Page -->
      <div class="database-page">
        <!-- Header + Camera Row -->
        <div class="database-header-camera">
          <!-- Database Info -->
          <div class="database-header">
            <h1 class="text-3xl font-bold mb-2">Database Management</h1>
            <div class="database-info">
              <p class="text-lg">
                <span class="font-semibold">Server:</span>
                <span class="server-name">{{ databaseInfo.serverName || 'Loading...' }}</span>
              </p>
              <p class="text-lg">
                <span class="font-semibold">Database:</span>
                <span class="database-name">{{ databaseInfo.databaseName || 'Loading...' }}</span>
              </p>
            </div>
          </div>

          <!-- Camera Feed -->
          <div class="database-camera">
            <h2 class="section-title">Live Camera Feed</h2>
            <div class="camera-container">
              <img :src="streamUrl" alt="Camera Stream" class="camera-stream" />
            </div>
          </div>
        </div>

        <!-- Two Column Layout: Collections & Details -->
        <div class="database-content">
          <!-- Left Box: Collections List -->
          <div class="collections-box">
            <h2 class="section-title">Data Collections</h2>
            <div class="collections-list">
              <div v-if="loading && collections.length === 0" class="text-center">
                <p class="text-gray-500">Loading collections...</p>
              </div>
              <div v-else-if="collections.length === 0" class="text-center">
                <p class="text-gray-500">No collections available</p>
              </div>
              <ul v-else class="collection-items">
                <li
                  v-for="collection in collections"
                  :key="collection.name"
                  :class="['collection-item', { active: selectedCollection === collection.name }]">
                  <div class="collection-info" @click="selectCollection(collection.name)">
                    <span class="collection-name">{{ collection.name }}</span>
                    <span class="collection-count">{{ collection.documentCount }} docs</span>
                  </div>
                  <button class="delete-btn" @click.stop="deleteCollection(collection.name)" title="Delete collection">
                    🗑️
                  </button>
                </li>
              </ul>
            </div>
          </div>

          <!-- Center Box: Selected Collection Display -->
          <div class="collection-detail-box">
            <h2 class="section-title">Collection Details</h2>

            <!-- Pagination Controls -->
            <div v-if="selectedCollection && !loading && !error && collectionData.length > 0" class="pagination-controls">
              <div class="page-size-selector">
                <label for="pageSize" class="page-size-label">Show:</label>
                <select id="pageSize" v-model="pageSize" @change="changePageSize" class="page-size-select">
                  <option :value="5">5</option>
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <span class="page-size-label">per page</span>
              </div>

              <div class="pagination-nav">
                <button class="pagination-btn" @click="previousPage" :disabled="currentPage <= 1">← Previous</button>
                <span class="pagination-info">Page {{ currentPage }} of {{ totalPages }} ({{ totalDocuments }} total docs)</span>
                <button class="pagination-btn" @click="nextPage" :disabled="currentPage >= totalPages">Next →</button>
              </div>
            </div>

            <div class="collection-display">
              <div v-if="!selectedCollection" class="text-center">
                <p class="text-gray-500">Select a collection to view details</p>
              </div>
              <div v-else-if="loading" class="text-center">
                <p class="text-gray-500">Loading data...</p>
              </div>
              <div v-else-if="error" class="text-center">
                <p class="text-red-500">{{ error }}</p>
              </div>
              <div v-else-if="collectionData.length === 0" class="text-center">
                <p class="text-gray-500">No data in this collection</p>
              </div>
              <div v-else class="data-display">
                <div class="document-grid">
                  <div v-for="(doc, index) in collectionData" :key="doc._id || index" class="document-card">
                    <div class="document-header">
                      <span class="document-id">{{ doc._id }}</span>
                    </div>
                    <div class="document-body">
                      <div v-for="(value, key) in doc" :key="key" class="document-field">
                        <span class="field-key">{{ key }}:</span>
                        <div class="field-value-container">
                          <span class="field-value" :class="{ 'collapsed': shouldTruncate(value) && !isFieldExpanded(doc._id, key) }">
                            {{ isFieldExpanded(doc._id, key) ? formatValue(value) : getTruncatedText(value) }}
                          </span>
                          <button v-if="shouldTruncate(value)" @click="toggleFieldExpansion(doc._id, key)" class="expand-btn">
                            {{ isFieldExpanded(doc._id, key) ? 'Show less' : 'Show more' }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div> <!-- End database-content -->
      </div> <!-- End database-page -->
    </main>
  </div>
</template>


<script>
app.component("databases", {
  template: "#databases",
  data() {
    return {
      sidebarOpen: true,
      username: '',
      streamUrl: 'http://192.168.1.209:5000/video',

      // Database information
      databaseInfo: {
        serverName: '',
        databaseName: ''
      },
      // Collections data
      collections: [],
      selectedCollection: null,
      collectionData: [],
      // Pagination state
      currentPage: 1,
      pageSize: 10,
      totalPages: 0,
      totalDocuments: 0,
      // UI state
      loading: false,
      error: null,
      // Track expanded state for each field in each document
      expandedFields: {},
      // Toast notification state
      toast: {
        show: false,
        message: '',
        type: 'success'
      },
      // Delete confirmation modal state
      deleteModalCollection: null
    };
  },

  methods: {
    showToast(message, type = 'success') {
      this.toast.message = message;
      this.toast.type = type;
      this.toast.show = true;
      setTimeout(() => {
        this.toast.show = false;
      }, 3000);
    },
    toggleButton() {
      this.sidebarOpen = !this.sidebarOpen
    },
    navigateToHome() {
      window.location.href = '/pages/home';
    },

    async getMe() {
      try {
        const response = await axios.post('/api/me');
        this.username = response.data.username;
      } catch (e) {
        console.error('Failed to get user: ', e);
      }
    },

    async logout() {
      try {
        await axios.get('/api/logout');
        window.location.href = '/pages/login';
      } catch (e) {
        console.error('Logout failed: ', e);
      }
    },

    // DATABASE MANAGEMENT METHODS
    // Fetches database server and connection information from backend
    async getDatabaseInfo() {
      try {
        this.loading = true;
        const response = await axios.get('/api/getDatabaseInfo');
        this.databaseInfo = response.data;
      } catch (e) {
        console.error('Failed to get database info: ', e);
        this.error = 'Failed to load database information';
      } finally {
        this.loading = false;
      }
    },

    // Fetches list of all collections from backend
    async getCollections() {
      try {
        this.loading = true;
        const response = await axios.get('/api/getCollections');
        this.collections = response.data;
      } catch (e) {
        console.error('Failed to get collections: ', e);
        this.error = 'Failed to load collections';
      } finally {
        this.loading = false;
      }
    },
    selectCollection(collectionName) {
      this.selectedCollection = collectionName;
      this.currentPage = 1; // Reset to first page when selecting a new collection
      this.getCollectionData(collectionName);
    },

    // Fetches documents from a specific collection with pagination
    async getCollectionData(collectionName) {
      try {
        this.loading = true;
        this.error = null;
        const response = await axios.get(`/api/getCollectionData/${collectionName}`, {
          params: {
            page: this.currentPage,
            pageSize: this.pageSize
          }
        });
        // Extract paginated data from response
        this.collectionData = response.data.documents;
        this.currentPage = response.data.currentPage;
        this.totalPages = response.data.totalPages;
        this.totalDocuments = response.data.totalDocuments;
      } catch (e) {
        console.error('Failed to get collection data: ', e);
        this.error = `Failed to load data from ${collectionName}`;
      } finally {
        this.loading = false;
      }
    },

    // Pagination controls
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.getCollectionData(this.selectedCollection);
      }
    },

    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.getCollectionData(this.selectedCollection);
      }
    },

    changePageSize() {
      // Reset to first page when changing page size
      this.currentPage = 1;
      this.getCollectionData(this.selectedCollection);
    },

    deleteCollection(collectionName) {
      this.deleteModalCollection = collectionName;
    },

    async confirmDelete() {
      const collectionName = this.deleteModalCollection;
      this.deleteModalCollection = null;

      try {
        await axios.delete(`/api/deleteCollection/${collectionName}`);
        // Refresh the collections list
        await this.getCollections();
        // Clear selection if the deleted collection was selected
        if (this.selectedCollection === collectionName) {
          this.selectedCollection = null;
          this.collectionData = [];
        }
        this.showToast('Collection was deleted successfully');
      } catch (e) {
        console.error('Failed to delete collection: ', e);
        this.showToast('Failed to delete collection. Please try again.', 'error');
      }
    },

    // Formats field values for display
    formatValue(value) {
      if (value === null || value === undefined) return 'null';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      if (typeof value === 'object') return JSON.stringify(value);
      return String(value);
    },

    // Check if a field value should be truncated
    shouldTruncate(value, maxLength = 150) {
      const stringValue = this.formatValue(value);
      return stringValue.length > maxLength;
    },

    // Get truncated text for display
    getTruncatedText(value, maxLength = 150) {
      const stringValue = this.formatValue(value);
      if (stringValue.length <= maxLength) {
        return stringValue;
      }
      return stringValue.substring(0, maxLength) + '...';
    },

    // Toggle expanded state for a specific field
    toggleFieldExpansion(docId, fieldKey) {
      const key = `${docId}_${fieldKey}`;
      this.expandedFields[key] = !this.expandedFields[key];
    },

    // Check if a field is expanded
    isFieldExpanded(docId, fieldKey) {
      const key = `${docId}_${fieldKey}`;
      return this.expandedFields[key] || false;
    },

  },

  async mounted() {
    this.getMe();
    this.getDatabaseInfo();
    this.getCollections();
  },


});
</script>

<style>

html, body, #main-vue {
  height: 100%;
  margin: 0;
}

.app-container {
  display: flex;
  height: 100%;
  font-family: sans-serif;
  color: #fff;
}

.sidebar {
  width: 260px;
  background-color: #202123;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 60px;
  padding: 20px 10px;
}

.sidebar-header {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
  margin-bottom: 5px;
  font-size: 1.5em;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-align: center;
}

.sidebar-subheader {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-align: center;
}

.icon-only {
  font-size: 1.6em;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  line-height: 1.4;
}

.menu-item:hover {
  background-color: #353740;
}

.menu-item.active {
  background-color: #444654;
}

.icon {
  font-size: 1.2em;
  min-width: 20px;
  text-align: center;
}

.label {
  white-space: nowrap;
}

.main-content {
  flex: 1;
  padding: 40px;
  position: relative;
  background-color: #f3f4f6;
  color: #111827;
  overflow: auto;
}

.toggle-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: #444654;
  border: none;
  color: #fff;
  padding: 10px 14px;
  font-size: 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.toggle-btn:hover {
  background-color: #55576a;
}

.logout-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #b91c1c;
}

/* Database Page Styling */
.database-page {
  max-width: 1400px;
  margin: 80px auto;
  padding: 0 20px;
}

.database-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.database-header h1 {
  color: #111827;
  margin-bottom: 20px;
}

.database-info {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 15px;
}

.database-info p {
  color: #374151;
}

.server-name,
.database-name {
  color: #2563eb;
  font-weight: 600;
}

/* Two Column Layout */
.database-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  margin-top: 30px;
}

.collections-box,
.collection-detail-box {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 25px;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e5e7eb;
  text-align: center;
}

.collections-list,
.collection-display {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 600px;
}

.collection-detail-box .collection-display {
  max-height: calc(600px - 60px);
}

/* Utility Classes */
.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.text-gray-500 {
  color: #6b7280;
}

.text-red-500 {
  color: #ef4444;
}

.text-center {
  text-align: center;
}

/* Collection Items Styling */
.collection-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.collection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.collection-item:hover {
  background: #e0f2fe;
  border-color: #0ea5e9;
}

.collection-item.active {
  background: #0ea5e9;
  color: white;
  border-color: #0284c7;
}

.collection-item.active .collection-count {
  color: rgba(255, 255, 255, 0.8);
}

.collection-name {
  font-weight: 600;
  font-size: 14px;
}

.collection-count {
  font-size: 12px;
  color: #64748b;
}

.collection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  cursor: pointer;
}

.delete-btn {
  background: none;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease, transform 0.2s ease;
  font-size: 14px;
}

.delete-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.collection-item.active .delete-btn {
  opacity: 0.8;
}

.collection-item.active .delete-btn:hover {
  opacity: 1;
}

/* Data Display Styling */
.data-display {
  padding: 10px;
  overflow: auto;
}

/* Document Grid and Cards */
.document-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.document-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.document-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.document-header {
  background: #f3f4f6;
  padding: 10px 15px;
  border-bottom: 1px solid #e5e7eb;
}

.document-id {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #6b7280;
  font-weight: 600;
}

.document-body {
  padding: 15px;
}

.document-field {
  display: flex;
  padding: 6px 0;
  border-bottom: 1px solid #f3f4f6;
}

.document-field:last-child {
  border-bottom: none;
}

.field-key {
  font-weight: 600;
  color: #374151;
  min-width: 120px;
  font-size: 13px;
}

.field-value-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-value {
  color: #6b7280;
  font-size: 13px;
  word-break: break-word;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.field-value.collapsed {
  overflow: hidden;
  text-overflow: ellipsis;
}

.expand-btn {
  align-self: flex-start;
  background: none;
  border: none;
  color: #0ea5e9;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
  text-decoration: none;
  transition: color 0.2s ease;
}

.expand-btn:hover {
  color: #0284c7;
  text-decoration: underline;
}

/* Pagination Controls */
.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 15px 20px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 15px;
  border: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 10;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.page-size-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.page-size-select:hover {
  border-color: #0ea5e9;
}

.page-size-select:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.pagination-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.pagination-btn {
  padding: 8px 16px;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #0284c7;
}

.pagination-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

/* Toast Notification Styling */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: rgba(34, 197, 94, 0.85);
  color: white;
  padding: 16px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  min-width: 300px;
  text-align: center;
}

/* Error Toast Variant */
.toast-notification.error {
  background-color: rgba(239, 68, 68, 0.85);
}

/* Toast Fade Animation */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Delete Confirmation Modal Styling */
.delete-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
}

.delete-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.delete-modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 16px;
}

.delete-modal-message {
  font-size: 1rem;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.5;
}

.delete-modal-message strong {
  color: #dc2626;
}

.delete-modal-warning {
  font-size: 0.875rem;
  color: #111827;
  font-weight: 700;
  margin-bottom: 24px;
}

.delete-modal-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.delete-modal-btn {
  padding: 12px 32px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-modal-btn-no {
  background-color: #e5e7eb;
  color: #374151;
}

.delete-modal-btn-no:hover {
  background-color: #d1d5db;
}

.delete-modal-btn-yes {
  background-color: #dc2626;
  color: white;
}

.delete-modal-btn-yes:hover {
  background-color: #b91c1c;
}

/* Header + Camera row */
.database-header-camera {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  margin-bottom: 30px;
  flex-wrap: wrap; /* allows responsive stacking on small screens */
}

/* Camera feed */
.database-camera {
  background: white;
  padding: 20px;
  border-radius: 8px;
  flex: 1;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.camera-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.camera-stream {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ccc;
  object-fit: contain;
}


</style>