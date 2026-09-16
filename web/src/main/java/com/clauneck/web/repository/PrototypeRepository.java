package com.clauneck.web.repository;

import com.clauneck.web.entity.Prototype;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PrototypeRepository extends JpaRepository<Prototype, Long> {
    Page<Prototype> findAllByOrderByCreatedAtDesc(Pageable pageable);
}
