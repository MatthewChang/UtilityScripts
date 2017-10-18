# different locks only lock on updated rows, locks are held until the end of the block
# other threads block when trying to write those rows
def different_locks_different_data
  threads = []
  FactoryGirl.create(:chat_message, session: Session.first)
  FactoryGirl.create(:chat_message, session: Session.second)
  ChatMessage.destroy_all
  threads << Thread.new do
    Session.first.with_lock do
      puts 'start'
      sleep 1
      # accessing different rows in the same table doesn't block
      ChatMessage.where(session: Session.first).destroy_all
      puts 'finishing'
      sleep 20
      puts 'done'
    end
  end

  threads << Thread.new do
    Session.second.with_lock do
      puts 'start2'
      sleep 1
      ChatMessage.where(session: Session.first).destroy_all
      puts 'finishing2'
      sleep 20
      puts 'done2'
    end
  end
  threads.each(&:join)
end

# different locks only lock on updated rows, locks are held until the end of the block
# other threads block when trying to write those rows
def different_locks_no_data
  threads = []
  ChatMessage.destroy_all
  threads << Thread.new do
    Session.first.with_lock do
      puts 'start'
      sleep 1
      # no messages here so no blocking
      ChatMessage.destroy_all
      ChatMessage.count
      puts 'finishing'
      sleep 20
      puts 'done'
    end
  end

  threads << Thread.new do
    Session.second.with_lock do
      puts 'start2'
      sleep 1
      ChatMessage.destroy_all
      ChatMessage.count
      puts 'finishing2'
      sleep 20
      puts 'done2'
    end
  end
  threads.each(&:join)
end

# different locks only lock on updated rows, locks are held until the end of the block
# other threads block when trying to write those rows
def different_locks
  threads = []
  FactoryGirl.create(:chat_message, session: Session.first)
  threads << Thread.new do
    Session.first.with_lock do
      puts 'start'
      sleep 1
      # ChatMessage.where(session_id: 1).destroy_all
      ChatMessage.destroy_all
      puts 'finishing'
      sleep 20
      puts 'done'
    end
  end

  threads << Thread.new do
    Session.second.with_lock do
      puts 'start2'
      sleep 1
      # ChatMessage.where(session_id: 2).destroy_all
      ChatMessage.destroy_all
      puts 'finishing2'
      sleep 20
      puts 'done2'
    end
  end
  threads.each(&:join)
end

# aquiring the same lock creates mutex
def same_lock
  threads = []
  threads << Thread.new do
    Session.first.with_lock do
      puts 'start'
      sleep 5
    end
  end

  threads << Thread.new do
    Session.first.with_lock do
      puts 'start2'
      sleep 5
    end
  end
  threads.each(&:join)
end

# can deadlock
def deadlock
  threads = []
  threads << Thread.new do
    Session.first.with_lock do
      puts 'start'
      sleep 5
      Session.second.destroy
      puts 'finish'
    end
  end

  threads << Thread.new do
    Session.second.with_lock do
      puts 'start2'
      sleep 5
      Session.first.destroy
      puts 'finish'
    end
  end
  threads.each(&:join)
end

deadlock
