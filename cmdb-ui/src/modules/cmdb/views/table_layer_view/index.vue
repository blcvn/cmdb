<template>
  <div class="table-layer-view-wrap" :style="{ height: `${windowHeight - 96}px` }">
    <SplitPane
      :min="180"
      :max="300"
      :paneLengthPixel.sync="paneLengthPixel"
      appName="cmdb-table-layer-view"
      :triggerLength="18"
      calcBasedParent
    >
      <template #one>
        <div class="table-layer-left">
          <div class="table-layer-left-title">
            <span style="font-weight: 700; font-size: 14px;">{{ $t('cmdb.tableLayer.tables') || 'Tables' }}</span>
          </div>
          <div class="table-layer-left-content">
            <div
              :class="`table-layer-item ${selectedTable === 'Example' ? 'selected' : ''}`"
              @click="handleSelectTable('Example')"
            >
              <span>Example</span>
            </div>
          </div>
        </div>
      </template>
      <template #two>
        <div class="table-layer-right">
          <h4 style="font-size: 16px; font-weight: 700; margin-bottom: 16px;">Example Application</h4>
          <a-table
            :columns="columns"
            :data-source="processedTableData"
            :pagination="false"
            :scroll="{ y: windowHeight - 220 }"
            size="small"
            row-key="key"
            bordered
          >
            <template slot="layer" slot-scope="text">
              <span style="font-weight: 600;">{{ text }}</span>
            </template>
            <template slot="ciType" slot-scope="text">
              <span>{{ text || '' }}</span>
            </template>
            <template slot="dc" slot-scope="text">
              <span>{{ text || '' }}</span>
            </template>
            <template slot="dr" slot-scope="text">
              <span>{{ text || '' }}</span>
            </template>
            <template slot="test" slot-scope="text">
              <span>{{ text || '' }}</span>
            </template>
          </a-table>
        </div>
      </template>
    </SplitPane>
  </div>
</template>

<script>
import SplitPane from '@/components/SplitPane'

export default {
  name: 'TableLayerView',
  components: {
    SplitPane
  },
  data() {
    return {
      paneLengthPixel: 250,
      selectedTable: 'Example',
      tableData: [
                // App Layer - Application
        {
          key: 'app-1',
          layer: 'App',
          ciType: 'Application',
          ciName: 'Example Application',
          dc: 'Example Application',
          dr: '',
          test: '',
          layerRowSpan: 1,
          ciTypeRowSpan: 1
        },
        {
          key: 'site',
          layer: 'Site',
          ciType: 'Site',
          ciName: 'data-center',
          dc: 'VNPAY',
          dr: 'CMC',
          test: 'TEST',
          layerRowSpan: 1,
          ciTypeRowSpan: 1
        },
        // App Service Layer - Mỗi CI instance một dòng
        {
          key: 'app-service-1',
          layer: 'App Service',
          ciType: 'Application Service',
          ciName: 'chiho-web-dc-01',
          dc: 'chiho-web-dc-01',
          dr: 'chiho-web-dr-01',
          test: 'chiho-web-test-01',
          layerRowSpan: 11, // Tổng 11 App Service
          ciTypeRowSpan: 11 // Tất cả đều là Application Service
        },
        {
          key: 'app-service-2',
          layer: 'App Service',
          ciType: 'Application Service',
          ciName: 'chiho-web-dc-02',
          dc: 'chiho-web-dc-02',
          dr: 'chiho-web-dr-02',
          test: 'chiho-web-test-02',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        {
          key: 'app-service-5',
          layer: 'App Service',
          ciType: 'Application Service',
          ciName: 'chiho-api-dc-01',
          dc: 'chiho-api-dc-01',
          dr: 'chiho-api-dr-01',
          test: 'chiho-api-test-01',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        {
          key: 'app-service-8',
          layer: 'App Service',
          ciType: 'Application Service',
          ciName: 'chiho-job-transaction-dc',
          dc: 'chiho-job-transaction-dc',
          dr: 'chiho-job-transaction-dr',
          test: '',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        {
          key: 'app-service-10',
          layer: 'App Service',
          ciType: 'Application Service',
          ciName: 'chiho-job-sync-dc',
          dc: 'chiho-job-sync-dc',
          dr: 'chiho-job-sync-dr',
          test: '',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        // Middleware Layer - Database
        {
          key: 'middleware-1',
          layer: 'Middleware',
          ciType: 'Database',
          ciName: 'mysql-db-dc-primary',
          dc: 'mysql-db-dc-primary',
          dr: 'mysql-db-dr-primary',
          test: 'mysql-db-test',
          layerRowSpan: 11, // Tổng 11 Middleware
          ciTypeRowSpan: 4 // 4 Database
        },
        {
          key: 'middleware-2',
          layer: 'Middleware',
          ciType: 'Database',
          ciName: 'mysql-db-dc-replica',
          dc: 'mysql-db-dc-replica',
          dr: 'mysql-db-dr-replica',
          test: '',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        // Middleware Layer - Cache
        {
          key: 'middleware-5',
          layer: 'Middleware',
          ciType: 'Cache',
          ciName: 'redis-cache-dc-01',
          dc: 'redis-cache-dc-01',
          dr: 'redis-cache-dr-01',
          test: 'redis-cache-test-01',
          layerRowSpan: 0,
          ciTypeRowSpan: 4 // 4 Cache
        },
        {
          key: 'middleware-6',
          layer: 'Middleware',
          ciType: 'Cache',
          ciName: 'redis-cache-dc-02',
          dc: 'redis-cache-dc-02',
          dr: 'redis-cache-dr-02',
          test: 'redis-cache-test-02',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        {
          key: 'middleware-7',
          layer: 'Middleware',
          ciType: 'Cache',
          ciName: 'redis-cache-dr-01',
          dc: 'redis-cache-dc-03',
          dr: 'redis-cache-dr-03',
          test: 'redis-cache-test-03',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        // Middleware Layer - Queue
        {
          key: 'middleware-9',
          layer: 'Middleware',
          ciType: 'Queue',
          ciName: 'rabbitmq-queue-dc-01',
          dc: 'rabbitmq-queue-dc-01',
          dr: 'rabbitmq-queue-dr-01',
          test: 'rabbitmq-queue-test-01',
          layerRowSpan: 0,
          ciTypeRowSpan: 3 // 3 Queue
        },
        {
          key: 'middleware-10',
          layer: 'Middleware',
          ciType: 'Queue',
          ciName: 'rabbitmq-queue-dc-02',
          dc: 'rabbitmq-queue-dc-02',
          dr: 'rabbitmq-queue-dr-02',
          test: 'rabbitmq-queue-test-02',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        // System Layer - Virtual Machine
        {
          key: 'system-1',
          layer: 'System',
          ciType: 'Virtual Machine',
          ciName: 'vm-dc-01',
          dc: 'vm-dc-01 (192.168.1.10)',
          dr: 'vm-dr-01 (192.168.2.10)',
          test: 'vm-test-01 (192.168.3.10)',
          layerRowSpan: 4, // Tổng 4 System
          ciTypeRowSpan: 2 // 2 Virtual Machine
        },
        {
          key: 'system-2',
          layer: 'System',
          ciType: 'Virtual Machine',
          ciName: 'vm-dc-02',
          dc: 'vm-dc-02 (192.168.1.11)',
          dr: 'vm-dr-02 (192.168.2.11)',
          test: 'vm-test-02 (192.168.3.11)',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        },
        // System Layer - IP
        {
          key: 'system-3',
          layer: 'System',
          ciType: 'IP',
          ciName: 'ip-dc-01',
          dc: '10.0.1.100',
          dr: '10.0.2.100',
          test: '10.0.3.100',
          layerRowSpan: 0,
          ciTypeRowSpan: 2 // 2 IP
        },
        {
          key: 'system-4',
          layer: 'System',
          ciType: 'IP',
          ciName: 'ip-dc-02',
          dc: '10.0.1.101',
          dr: '10.0.2.101',
          test: '10.0.3.101',
          layerRowSpan: 0,
          ciTypeRowSpan: 0
        }
      ],
      columns: [
        {
          title: this.$t('cmdb.tableLayer.layer') || 'Layer',
          dataIndex: 'layer',
          key: 'layer',
          width: 150,
          customCell: (record, rowIndex) => {
            return {
              rowSpan: record.layerRowSpan || 1
            }
          },
          scopedSlots: { customRender: 'layer' }
        },
        {
          title: this.$t('cmdb.tableLayer.name') || 'CI Type',
          dataIndex: 'ciType',
          key: 'ciType',
          width: 200,
          customCell: (record) => {
            return {
              rowSpan: record.ciTypeRowSpan
            }
          },
          scopedSlots: { customRender: 'ciType' }
        },
        {
          title: this.$t('cmdb.tableLayer.ci') || 'CI',
          key: 'ci',
          children: [
            {
              title: 'DC',
              dataIndex: 'dc',
              key: 'dc',
              scopedSlots: { customRender: 'dc' }
            },
            {
              title: 'DR',
              dataIndex: 'dr',
              key: 'dr',
              scopedSlots: { customRender: 'dr' }
            },
            {
              title: 'Test',
              dataIndex: 'test',
              key: 'test',
              scopedSlots: { customRender: 'test' }
            }
          ]
        }
      ]
    }
  },
  computed: {
    windowHeight() {
      return this.$store.state.windowHeight
    },
    processedTableData() {
      // Calculate rowSpan automatically based on layer grouping
      if (!this.tableData || this.tableData.length === 0) {
        return []
      }

      // First pass: calculate rowSpan for each row
      const result = this.tableData.map((row, index) => {
        const prevRow = index > 0 ? this.tableData[index - 1] : null
        const isFirstOfLayer = !prevRow || prevRow.layer !== row.layer

        if (isFirstOfLayer) {
          // Count consecutive rows with same layer
          let count = 1
          for (let i = index + 1; i < this.tableData.length; i++) {
            if (this.tableData[i].layer === row.layer) {
              count++
            } else {
              break
            }
          }
          return {
            ...row,
            layerRowSpan: count
          }
        } else {
          return {
            ...row,
            layerRowSpan: 0
          }
        }
      })

      return result
    }
  },
  mounted() {
    // Initialize
  },
  methods: {
    handleSelectTable(tableName) {
      this.selectedTable = tableName
      // TODO: Load table data when selecting different table
    }
  }
}
</script>

<style lang="less" scoped>
.table-layer-view-wrap {
  margin: 0 0 -24px 0;

  .table-layer-left {
    width: 100%;
    height: 100%;
    overflow: auto;
    float: left;

    .table-layer-left-title {
      padding: 10px 14px;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      color: @text-color_3;
      border-bottom: 1px solid #e8e8e8;
    }

    .table-layer-left-content {
      max-height: calc(100% - 45px);
      overflow: hidden;
      &:hover {
        overflow: auto;
      }
    }

    .table-layer-item {
      padding: 8px 14px;
      color: rgb(99, 99, 99);
      cursor: pointer;
      font-size: 14px;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;

      &:hover {
        background-color: @primary-color_3;
      }

      &.selected {
        background-color: @primary-color_3;
        font-weight: 700;
      }
    }
  }

  .table-layer-right {
    width: 100%;
    height: 100%;
    position: relative;
    background-color: #fff;
    padding: 20px;
  }
}
</style>
