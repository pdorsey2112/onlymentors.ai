import React from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { 
  User, 
  Star, 
  Award, 
  BookOpen, 
  Calendar,
  MapPin,
  ExternalLink,
  X
} from 'lucide-react';

const MentorProfileModal = ({ mentor, isOpen, onClose, onSelect, isSelected, user }) => {
  if (!mentor) return null;

  const handleSelect = () => {
    onSelect(mentor);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl font-bold text-gray-900">
              {mentor.name}
            </DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <DialogDescription className="text-purple-600 font-medium">
            {mentor.title}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Hero Section */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Avatar className="w-24 h-24 sm:w-32 sm:h-32 mx-auto sm:mx-0">
              {mentor.image_url ? (
                <AvatarImage 
                  src={mentor.image_url} 
                  alt={mentor.name}
                  className="object-cover w-full h-full"
                />
              ) : (
                <AvatarFallback className="bg-purple-100 text-purple-600 text-2xl font-bold">
                  <User className="h-16 w-16" />
                </AvatarFallback>
              )}
            </Avatar>
            
            <div className="flex-1 space-y-3">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">About</h3>
                <p className="text-gray-700 leading-relaxed">
                  {mentor.bio || `${mentor.name} is a renowned expert in ${mentor.expertise}. With extensive experience and proven track record, they offer valuable insights and guidance to help you achieve your goals.`}
                </p>
              </div>
              
              {user && (
                <Button 
                  onClick={handleSelect}
                  className={`w-full sm:w-auto ${
                    isSelected 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-purple-600 hover:bg-purple-700'
                  }`}
                >
                  <Star className="h-4 w-4 mr-2" />
                  {isSelected ? 'Selected for Questions' : 'Select for Questions'}
                </Button>
              )}
            </div>
          </div>

          {/* Expertise Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Award className="h-5 w-5 text-purple-600" />
              Areas of Expertise
            </h3>
            <div className="flex flex-wrap gap-2">
              {mentor.expertise.split(', ').map((skill, index) => (
                <Badge 
                  key={index} 
                  variant="secondary" 
                  className="bg-purple-100 text-purple-700 px-3 py-1"
                >
                  {skill.trim()}
                </Badge>
              ))}
            </div>
          </div>

          {/* Wikipedia Description */}
          {mentor.wiki_description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-purple-600" />
                Biography
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 leading-relaxed">
                  {mentor.wiki_description}
                </p>
                {mentor.wiki_url && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <a 
                      href={mentor.wiki_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-purple-600 hover:text-purple-800 text-sm font-medium"
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      Learn more on Wikipedia
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Key Achievements */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Star className="h-5 w-5 text-purple-600" />
              Why Ask {mentor.name.split(' ')[0]}?
            </h3>
            <div className="grid gap-3">
              <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                <div className="bg-purple-100 p-1 rounded">
                  <Award className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Expert Knowledge</h4>
                  <p className="text-gray-600 text-sm">Deep expertise in {mentor.expertise.split(', ')[0]} and related fields</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                <div className="bg-purple-100 p-1 rounded">
                  <BookOpen className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Real-World Experience</h4>
                  <p className="text-gray-600 text-sm">Practical insights from years of hands-on experience</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                <div className="bg-purple-100 p-1 rounded">
                  <Star className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Proven Track Record</h4>
                  <p className="text-gray-600 text-sm">Established success and recognition in their field</p>
                </div>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          {user && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
              <div className="text-center">
                <h4 className="font-semibold text-gray-900 mb-2">Ready to get guidance from {mentor.name.split(' ')[0]}?</h4>
                <p className="text-gray-600 text-sm mb-4">Select this mentor and ask your questions to receive personalized advice</p>
                <Button 
                  onClick={handleSelect}
                  className={`${
                    isSelected 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-purple-600 hover:bg-purple-700'
                  }`}
                  size="lg"
                >
                  <Star className="h-4 w-4 mr-2" />
                  {isSelected ? 'Already Selected' : 'Select This Mentor'}
                </Button>
              </div>
            </div>
          )}

          {!user && (
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 text-center">
              <h4 className="font-semibold text-gray-900 mb-2">Want guidance from {mentor.name.split(' ')[0]}?</h4>
              <p className="text-gray-600 text-sm mb-3">Create a free account to ask questions and get personalized advice</p>
              <Button onClick={onClose} variant="outline">
                Close Profile
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default MentorProfileModal;