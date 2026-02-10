import React, { useState } from 'react';

interface FlowState {
  currentFocus: {
    name: string;
    value: number;
    deadline: string;
    daysLeft: number;
  } | null;
  nextAction: string;
  stepNumber: number;
  totalSteps: number;
  urgentCount: number;
  todayCompleted: number;
}

export const BidsFlow: React.FC = () => {
  const [flow, setFlow] = useState<FlowState>({
    currentFocus: null,
    nextAction: '',
    stepNumber: 0,
    totalSteps: 0,
    urgentCount: 0,
    todayCompleted: 0
  });

  const openFolder = () => {
    console.log('Opening folder...');
    // In production: window.api.openFolder(...)
  };

  const markComplete = () => {
    if (flow.stepNumber < flow.totalSteps) {
      setFlow({
        ...flow,
        stepNumber: flow.stepNumber + 1,
        nextAction: getNextAction(flow.stepNumber + 1),
        todayCompleted: flow.todayCompleted + 1
      });
    } else {
      // Move to next bid
      alert('Bid complete! Moving to next priority...');
    }
  };

  const getNextAction = (step: number): string => {
    const actions = [
      'Open bid folder and check for analysis document',
      'Find battery cabinet suppliers',
      'Request quotes from suppliers',
      'Review quotes and prepare bid package',
      'Submit bid by Wednesday 2:00 PM'
    ];
    return actions[step - 1] || 'Complete!';
  };

  if (!flow.currentFocus) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">✅</div>
          <div className="text-2xl font-bold text-white mb-2">All caught up!</div>
          <div className="text-gray-400">No urgent bids right now</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Step {flow.stepNumber} of {flow.totalSteps}</span>
            <span className="text-sm text-gray-400">{flow.urgentCount} urgent remaining</span>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${(flow.stepNumber / flow.totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Focus Card */}
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 shadow-2xl">
          
          {/* Header */}
          <div className="mb-6">
            <div className="text-sm text-gray-400 mb-2">Your Focus Right Now</div>
            <h1 className="text-3xl font-bold text-white mb-2">
              {flow.currentFocus.name}
            </h1>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-green-400 font-semibold">
                ${(flow.currentFocus.value / 1000).toFixed(0)}K
              </span>
              <span className="text-gray-400">•</span>
              <span className={`font-semibold ${
                flow.currentFocus.daysLeft <= 2 ? 'text-red-400' : 'text-yellow-400'
              }`}>
                {flow.currentFocus.daysLeft} days left
              </span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-400">{flow.currentFocus.deadline}</span>
            </div>
          </div>

          {/* Next Action */}
          <div className="bg-gray-800/50 rounded-xl p-6 mb-6">
            <div className="text-sm text-gray-400 mb-3">Next Action:</div>
            <div className="text-xl text-white mb-4">
              {flow.nextAction}
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={openFolder}
                className="flex-1 px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition flex items-center justify-center gap-2"
              >
                <span>📂</span>
                <span>Open Folder</span>
              </button>
              <button
                onClick={markComplete}
                className="px-6 py-3 bg-green-500 hover:bg-green-600 rounded-lg font-semibold transition flex items-center justify-center gap-2"
              >
                <span>✓</span>
                <span>Done</span>
              </button>
            </div>
          </div>

          {/* Remaining Steps Preview */}
          <div className="border-t border-gray-700 pt-4">
            <div className="text-xs text-gray-500 mb-2">Coming up:</div>
            <div className="space-y-1">
              {flow.stepNumber < flow.totalSteps && (
                <>
                  <div className="text-sm text-gray-400 flex items-center gap-2">
                    <span className="text-gray-600">→</span>
                    <span>{getNextAction(flow.stepNumber + 1)}</span>
                  </div>
                  {flow.stepNumber < flow.totalSteps - 1 && (
                    <div className="text-sm text-gray-500 flex items-center gap-2">
                      <span className="text-gray-700">→</span>
                      <span>{getNextAction(flow.stepNumber + 2)}</span>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Today's Progress */}
        <div className="mt-6 text-center text-sm text-gray-400">
          Today: {flow.todayCompleted} steps completed
        </div>
      </div>
    </div>
  );
};
