import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const Battlecard = ({ battlecard }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-6 hover:shadow-xl transition-shadow">
      <div className="p-4 md:p-6">
        <div 
          className="flex justify-between items-start cursor-pointer"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <h3 className="text-lg md:text-xl font-semibold text-blue-600 flex-grow pr-4">
            {battlecard.problem_area}
          </h3>
          {isExpanded ? (
            <ChevronUp className="h-6 w-6 text-gray-400 flex-shrink-0" />
          ) : (
            <ChevronDown className="h-6 w-6 text-gray-400 flex-shrink-0" />
          )}
        </div>

        <div className={`mt-4 space-y-4 ${isExpanded ? 'block' : 'hidden'}`}>
          <div className="space-y-2">
            <h4 className="font-medium text-gray-700">Problem Description:</h4>
            <p className="text-gray-600 text-sm md:text-base leading-relaxed">
              {battlecard.problem_description}
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium text-gray-700">Solution & Differentiators:</h4>
            <p className="text-gray-600 text-sm md:text-base leading-relaxed">
              {battlecard.differentiator}
            </p>
          </div>

          {battlecard.case_studies && battlecard.case_studies.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">Case Studies:</h4>
              <ul className="space-y-3">
                {battlecard.case_studies.map((study, index) => (
                  <li 
                    key={index}
                    className="text-gray-600 text-sm md:text-base leading-relaxed pl-4 border-l-2 border-blue-200"
                  >
                    {study}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Battlecard;