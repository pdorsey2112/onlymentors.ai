import React from 'react';

const MentorTierBadge = ({ tier, level, badgeColor, description, size = "medium", showDescription = false }) => {
  const getTierIcon = (level) => {
    switch (level) {
      case 'ultimate':
        return '👑'; // Crown for Ultimate
      case 'platinum':
        return '💎'; // Diamond for Platinum
      case 'gold':
        return '🥇'; // Gold medal for Gold
      case 'silver':
        return '🥈'; // Silver medal for Silver
      case 'new':
        return '⭐'; // Star for New
      default:
        return '⭐';
    }
  };

  const getSizeClasses = (size) => {
    switch (size) {
      case 'small':
        return {
          container: 'px-2 py-1 text-xs',
          icon: 'text-sm',
          text: 'text-xs font-medium'
        };
      case 'large':
        return {
          container: 'px-4 py-2 text-base',
          icon: 'text-xl',
          text: 'text-base font-semibold'
        };
      case 'xlarge':
        return {
          container: 'px-6 py-3 text-lg',
          icon: 'text-2xl',
          text: 'text-lg font-bold'
        };
      default: // medium
        return {
          container: 'px-3 py-1.5 text-sm',
          icon: 'text-base',
          text: 'text-sm font-semibold'
        };
    }
  };

  const sizeClasses = getSizeClasses(size);
  const icon = getTierIcon(level);

  return (
    <div className="inline-flex items-center">
      <div 
        className={`inline-flex items-center rounded-full border-2 transition-all duration-200 ${sizeClasses.container}`}
        style={{ 
          backgroundColor: `${badgeColor}15`, // 15% opacity background
          borderColor: badgeColor,
          color: badgeColor
        }}
      >
        <span className={`mr-1 ${sizeClasses.icon}`}>{icon}</span>
        <span className={sizeClasses.text}>{tier}</span>
      </div>
      
      {showDescription && description && (
        <span className="ml-2 text-xs text-gray-500 italic">
          {description}
        </span>
      )}
    </div>
  );
};

export default MentorTierBadge;