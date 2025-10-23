#ifndef TAGE_CONFIG_H
#define TAGE_CONFIG_H

class tage_config {
public:
    static constexpr std::size_t NUMBER_OF_TABLES = 12;
    static constexpr uint16_t LEAST_HISTORY_LENGTH = 4;
    static constexpr double COMMON_RATIO = 1.5;

    static constexpr uint8_t TAG_SIZE_MAX = 10;
    static constexpr uint8_t TAG_SIZE_MIN = 6;

    static constexpr uint8_t MAX_TABLE_SIZE_LOG = 11;
    static constexpr uint8_t MIN_TABLE_SIZE_LOG = 9;

    enum class TableSizePattern {
        CONSTANT,
        ASCENDING,
        DESCENDING,
        HILL_SHAPED
    };

    static constexpr TableSizePattern ACTIVE_PATTERN = TableSizePattern::HILL_SHAPED;
};

#endif
